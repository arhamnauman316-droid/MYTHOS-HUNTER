import config, json
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

run_info = client.run("06YUVf8rv2NIY72BP").get()
items = list(client.dataset(run_info["defaultDatasetId"]).iterate_items())
for it in items[:3]:
    print("postedAt:", repr(it.get("postedAt")))
    print("query:", it.get("query"))
    print()
