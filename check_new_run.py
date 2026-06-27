import config, json
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

run_id = "T3MpxFi5Umq9LGqNe"
run_info = client.run(run_id).get()
ds_id = run_info["defaultDatasetId"]
items = list(client.dataset(ds_id).iterate_items())
print(f"Total items: {len(items)}")
for it in items:
    if it.get("error"):
        print("FAILED:", it)
        continue
    print(sorted(it.keys()))
    print(json.dumps(it, indent=2, default=str)[:800])
    print("---")
