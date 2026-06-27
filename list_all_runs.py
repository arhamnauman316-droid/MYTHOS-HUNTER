import config
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)
runs = client.actor("harvestapi/linkedin-profile-scraper").runs().list(limit=3, desc=True)
for r in runs.items:
    print(r["id"], r["status"], r.get("startedAt"))
print("---")
runs2 = client.actor("dev_fusion/linkedin-profile-scraper").runs().list(limit=5, desc=True)
for r in runs2.items:
    print(r["id"], r["status"], r.get("startedAt"))
