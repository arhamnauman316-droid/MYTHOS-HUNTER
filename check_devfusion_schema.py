import config
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

run_id = "mU5bbaZhqcgcDwlgl"
run_info = client.run(run_id).get()
print("INPUT used:", run_info.get("options", {}))
# fetch the actual input via the run's input record
import json
try:
    key_value_store_id = run_info["defaultKeyValueStoreId"]
    input_record = client.key_value_store(key_value_store_id).get_record("INPUT")
    print("RAW INPUT:", json.dumps(input_record["value"], indent=2))
except Exception as e:
    print("Could not fetch input record:", e)

ds_id = run_info["defaultDatasetId"]
items = list(client.dataset(ds_id).iterate_items())
print(f"\nThis run had {len(items)} output items. First item keys:")
if items:
    print(sorted(items[0].keys()))
    print(json.dumps(items[0], indent=2, default=str)[:1500])
