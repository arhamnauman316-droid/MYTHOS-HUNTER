import sys
sys.path.insert(0, r"C:\mythos-real")

import config
from apify_client import ApifyClient
from agent import process_lead
from sheets import SheetsClient

RUN_ID = "wa9pUDsxe9HcNk81a"

print(f"Connecting to Apify, fetching dataset from run {RUN_ID}...")
client = ApifyClient(config.APIFY_TOKEN)
run_info = client.run(RUN_ID).get()
dataset_id = run_info["defaultDatasetId"]
items = list(client.dataset(dataset_id).iterate_items())
print(f"Fetched {len(items)} items from the real scrape.")

valid_items = [i for i in items if not i.get("error") and i.get("status") not in (404, 400, 403)]
print(f"{len(valid_items)} are real, valid LinkedIn profiles (no errors/404s).")

from datetime import datetime, timezone
scraped_at_label = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
for item in valid_items:
    item["scraped_at"] = scraped_at_label

print("Processing through the real pipeline (parse, classify, draft message)...")
leads = [process_lead(item) for item in valid_items]
leads = [l for l in leads if l]

active = [l for l in leads if l.get("Status") == "Active"]
inactive = [l for l in leads if l.get("Status") == "Inactive"]

for l in leads:
    name = l["name"]
    status = l["Status"]
    activity = l["Recent Activity"]
    email = l.get("email") or "(none found)"
    print("  - " + name + ": " + status + ", Recent Activity: " + activity + ", Email: " + email)

print("Writing to Google Sheet live...")
sheets_client = SheetsClient()
if active:
    sheets_client.save_leads(active, "Active")
    sheets_client.save_messages(active)
if inactive:
    sheets_client.save_leads(inactive, "Inactive")

print(f"DONE. {len(active)} Active, {len(inactive)} Inactive written to the sheet.")
print("Check the sheet now -- this is real data from a real LinkedIn scrape.")
