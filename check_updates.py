import config, json
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

for run_id in ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]:
    run_info = client.run(run_id).get()
    items = list(client.dataset(run_info["defaultDatasetId"]).iterate_items())
    for it in items:
        if it.get("error"):
            continue
        name = it.get("fullName") or "?"
        updates = it.get("updates") or []
        print(f"\n=== {name} - {len(updates)} updates ===")
        if updates:
            print(json.dumps(updates[0], indent=2, default=str))
