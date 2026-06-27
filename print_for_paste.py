import sys
sys.path.insert(0, r"C:\mythos-real")

import config
from apify_client import ApifyClient
from agent import process_lead

RUN_ID = "wa9pUDsxe9HcNk81a"
client = ApifyClient(config.APIFY_TOKEN)
run_info = client.run(RUN_ID).get()
dataset_id = run_info["defaultDatasetId"]
items = list(client.dataset(dataset_id).iterate_items())
valid_items = [i for i in items if not i.get("error") and i.get("status") not in (404, 400, 403)]

leads = [process_lead(item) for item in valid_items]
leads = [l for l in leads if l]

print("=" * 70)
print("COPY THE LINES BELOW (between the === markers) INTO YOUR ACTIVE/INACTIVE TAB")
print("Click cell A2, paste -- Google Sheets will auto-split into columns")
print("=" * 70)
for l in leads:
    row = [
        l.get("name", ""), l.get("url", ""), l.get("email", ""),
        l.get("headline", ""), l.get("services", ""), l.get("about", ""),
        l.get("Recent Activity", ""), l.get("Status", ""),
        l.get("Commented On (Author)", ""), l.get("Commented Post Topic", ""),
        l.get("AI Draft Message", ""), l.get("Scraped At", "")
    ]
    print("\t".join(str(x) for x in row))
print("=" * 70)

print()
print("COPY THE LINES BELOW INTO YOUR MESSAGES TAB (click cell A2, paste)")
print("=" * 70)
for l in leads:
    row = [l.get("name", ""), l.get("url", ""), l.get("email", ""),
           l.get("AI Draft Message", ""), l.get("Scraped At", "")]
    print("\t".join(str(x) for x in row))
print("=" * 70)
