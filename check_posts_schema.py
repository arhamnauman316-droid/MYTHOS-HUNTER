import config, json
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

run_info = client.run("06YUVf8rv2NIY72BP").get()
items = list(client.dataset(run_info["defaultDatasetId"]).iterate_items())
print(f"Total post items: {len(items)}")
if items:
    print("Keys:", sorted(items[0].keys()))
    print(json.dumps(items[0], indent=2, default=str)[:1000])
