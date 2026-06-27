import config
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)
runs = client.actor("dev_fusion/linkedin-profile-scraper").runs().list(limit=10, desc=True)
for r in runs.items:
    print(r["id"], r["status"], r.get("startedAt"))
