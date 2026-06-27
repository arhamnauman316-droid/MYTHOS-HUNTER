import os
from apify_client import ApifyClient
import config

client = ApifyClient(config.APIFY_TOKEN)
runs = client.actor("harvestapi/linkedin-profile-scraper").runs().list(limit=20, desc=True)
for r in runs.items:
    print(r["id"], r["status"], r.get("startedAt"), "dataset:", r.get("defaultDatasetId"))
