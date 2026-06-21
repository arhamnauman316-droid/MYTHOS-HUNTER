import logging, config, re
from typing import Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from brightdata_client import BrightDataClient, parse_profile_data
from activity import parse_linkedin_date, classify_profile, humanize_days_ago
from drafter import draft_message
from sheets import SheetsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_date_from_interaction(interaction: str) -> Optional[str]:
    if not interaction:
        return None
    match = re.search(r'(\d+[dwmh])', interaction)
    if match:
        return match.group(1)
    return None

def extract_author_from_interaction(interaction: str) -> str:
    if not interaction:
        return "someone"
    interaction = interaction.lower()
    if "commented on" in interaction:
        parts = re.split(r'commented on', interaction)
        if parts:
            name = parts[0].strip().title()
            if name:
                return name
    return "someone"

def process_lead(raw_record):
    try:
        profile = parse_profile_data(raw_record)
        activity = profile.get("activity", [])
        last_date = None
        author = "someone"
        topic = "their recent post"

        for act in activity:
            interaction = act.get("interaction", "") or ""
            date_str = extract_date_from_interaction(interaction)
            if date_str:
                last_date = parse_linkedin_date(date_str)
                if last_date:
                    title = act.get("title", "")
                    if title:
                        topic = title[:120]
                    extracted_author = extract_author_from_interaction(interaction)
                    if extracted_author != "someone":
                        author = extracted_author
                    break

        # If no recent activity found, leave last_date as None to indicate no recent activity
        # This will result in an "Inactive" classification, which is more accurate than an arbitrary date
        pass

        status = classify_profile(last_date, config.ACTIVITY_WINDOW_DAYS)
        ai_draft = draft_message(profile["name"], author, topic)

        return {
            **profile,
            "Recent Activity": humanize_days_ago(last_date),
            "Status": status,
            "Commented On (Author)": author,
            "Commented Post Topic": topic[:150] if topic else "",
            "AI Draft Message": ai_draft,
            "Scraped At": profile.get("scraped_at", "")
        }
    except Exception as e:
        logger.error(f"Error processing lead: {e}")
        return None

def run():
    logger.info("Mythos Hunter starting...")
    bd_client = BrightDataClient()
    sheets_client = SheetsClient()
    niches = sheets_client.get_niches()
    logger.info(f"Found niches: {niches}")
    all_active = []
    all_inactive = []
    for niche in niches:
        logger.info(f"Hunting niche: {niche}")
        raw_results = bd_client.search_profiles(niche)
        if not raw_results:
            logger.info(f"No results for {niche}")
            continue
        with ThreadPoolExecutor(max_workers=5) as executor:
            leads = list(filter(None, executor.map(process_lead, raw_results)))
        for lead in leads:
            if lead.get("Status") == "Active":
                all_active.append(lead)
            else:
                all_inactive.append(lead)
        active_count = len([l for l in leads if l.get('Status') == 'Active'])
        inactive_count = len([l for l in leads if l.get('Status') == 'Inactive'])
        logger.info(f"Niche {niche}: {len(leads)} leads - Active: {active_count}, Inactive: {inactive_count}")
    if all_active:
        sheets_client.save_leads(all_active, "Active")
        sheets_client.save_messages(all_active)
    if all_inactive:
        sheets_client.save_leads(all_inactive, "Inactive")
    logger.info(f"Done. Active: {len(all_active)}, Inactive: {len(all_inactive)}")
    print(f"\nSheet URL: {sheets_client.sheet.url}")

if __name__ == "__main__":
    run()
