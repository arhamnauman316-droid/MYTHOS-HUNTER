runs = [
    "Pq1m1ljD8vnfliBN1", "X1FGAkyApsIL77D3s", "wa9pUDsxe9HcNk81a",
    "dlTNXAcvxOQFLoMPH", "03CQqtWHsrw2lpMFU", "iYAHOcAQazMP7ghFh",
    "f5dakt8CIatShhYs4", "KPwude4H4O6tER1Im", "xW5lA9xiJP2q3VoNB",
    "banBomR2MQdlStTvc", "gMErLy1bQjGYIV17t", "L17VcOjDLoWZ8iY0z",
]

import config
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

first_item_dumped = False

for run_id in runs:
    try:
        run_info = client.run(run_id).get()
        ds_id = run_info["defaultDatasetId"]
        items = list(client.dataset(ds_id).iterate_items())
        print(f"\n=== {run_id} ({len(items)} items) ===")
        for it in items:
            if it.get("error") or it.get("status") in (404, 400, 403):
                q = it.get("query") or {}
                print(f"  FAILED: {q.get('url', 'unknown')}")
                continue
            if not first_item_dumped:
                print("  >>> RAW KEYS OF FIRST VALID ITEM:", sorted(it.keys()))
                first_item_dumped = True
            name = it.get("fullName") or it.get("name") or "?"
            headline = (it.get("headline") or "")[:60]
            url = it.get("publicProfileUrl") or it.get("linkedinUrl") or it.get("url") or "?"
            print(f"  OK: {name} | {headline} | {url}")
    except Exception as e:
        print(f"\n=== {run_id}: ERROR {e} ===")
