import json, sys
sys.path.insert(0, r"C:\mythos-real")

from brightdata_client import parse_profile_data
from agent import process_lead
from sheets import SheetsClient

with open(r"C:\mythos-real\debug_raw.json", "r", encoding="utf-8") as f:
    items = json.load(f)

valid_items = [i for i in items if not i.get("error") and i.get("status") not in (404, 400, 403)]
print(f"Found {len(valid_items)} real, valid scraped profiles in debug_raw.json")

from datetime import datetime, timezone
scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC") + " (rebuilt from saved scrape)"
for item in valid_items:
    if not item.get("scraped_at"):
        item["scraped_at"] = scraped_at

leads = [process_lead(item) for item in valid_items]
leads = [l for l in leads if l]

active = [l for l in leads if l.get("Status") == "Active"]
inactive = [l for l in leads if l.get("Status") == "Inactive"]

print(f"Processed: {len(active)} Active, {len(inactive)} Inactive (honest classification, no fake fallback)")

sheets_client = SheetsClient()
if active:
    sheets_client.save_leads(active, "Active")
    sheets_client.save_messages(active)
if inactive:
    sheets_client.save_leads(inactive, "Inactive")

print("Done. Real data written to sheet.")
print("IMPORTANT: go delete the 2 fake mock rows (Sarah Jenkins, Michael Chen)")
print("from the Active and Messages tabs -- those are NOT real leads.")
