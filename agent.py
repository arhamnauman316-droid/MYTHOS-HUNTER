import logging, config
from concurrent.futures import ThreadPoolExecutor
from brightdata_client import BrightDataClient, parse_profile_data
from activity import parse_linkedin_date, classify_profile, humanize_days_ago
from drafter import draft_message
from sheets import SheetsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_lead(raw_record):
    try:
        profile = parse_profile_data(raw_record)
        activity = profile.get("activity", [])
        last_date = parse_linkedin_date(activity[0].get("date")) if activity else None
        status = classify_profile(last_date, config.ACTIVITY_WINDOW_DAYS)
        first_activity = activity[0] if activity else {}
        author = first_activity.get("post_author", "someone")
        topic = first_activity.get("post_topic", "their recent post")
        ai_draft = draft_message(profile["name"], author, topic)
        return {
            **profile,
            "Recent Activity": humanize_days_ago(last_date),
            "Status": status,
            "Commented On (Author)": author,
            "Commented Post Topic": topic,
            "AI Draft Message": ai_draft
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
        logger.info(f"Niche {niche}: {len(leads)} leads processed")
    if all_active:
        sheets_client.save_leads(all_active, "Active")
    if all_inactive:
        sheets_client.save_leads(all_inactive, "Inactive")
    logger.info(f"Done. Active: {len(all_active)}, Inactive: {len(all_inactive)}")
    print(f"\nSheet URL: {sheets_client.sheet.url}")

if __name__ == "__main__":
    run()
