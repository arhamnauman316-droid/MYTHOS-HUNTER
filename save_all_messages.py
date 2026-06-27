import sys
sys.path.insert(0, r"C:\mythos-real")

import config
from apify_client import ApifyClient
from agent import process_lead
from sheets import SheetsClient

RUN_ID = "wa9pUDsxe9HcNk81a"
client = ApifyClient(config.APIFY_TOKEN)
run_info = client.run(RUN_ID).get()
dataset_id = run_info["defaultDatasetId"]
items = list(client.dataset(dataset_id).iterate_items())
valid_items = [i for i in items if not i.get("error") and i.get("status") not in (404, 400, 403)]

leads = [process_lead(item) for item in valid_items]
leads = [l for l in leads if l]

print("Saving messages for ALL real leads (not just Active ones)...")
sheets_client = SheetsClient()
sheets_client.save_messages(leads)
print("Done -- check the Messages tab now.")
