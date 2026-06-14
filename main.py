import argparse, logging, csv, json, config
from concurrent.futures import ThreadPoolExecutor
from brightdata_client import BrightDataClient, parse_profile_data
from activity import parse_linkedin_date, classify_profile, humanize_days_ago
from drafter import draft_message
from sheets import SheetsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_niche(niche: str, dry_run: bool = False):
    bd_client, sheets_client = BrightDataClient(), SheetsClient()
    raw_results = bd_client.search_profiles(niche)
    if not raw_results: return

    def process_single_lead(raw_record):
        try:
            profile = parse_profile_data(raw_record)
            last_date = parse_linkedin_date(profile["activity"][0].get("date")) if profile["activity"] else None
            status = classify_profile(last_date, config.ACTIVITY_WINDOW_DAYS)
            ai_draft = draft_message(profile["name"], "someone", "topic")
            return {**profile, "Recent Activity": humanize_days_ago(last_date), "Status": status, "AI Draft Message": ai_draft}
        except: return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        leads = list(filter(None, executor.map(process_single_lead, raw_results)))
    
    if dry_run: print(json.dumps(leads, indent=2))
    else: sheets_client.save_leads(leads)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("niche", type=str)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    process_niche(args.niche, args.dry_run)
