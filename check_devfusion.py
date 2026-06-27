import config
from apify_client import ApifyClient
client = ApifyClient(config.APIFY_TOKEN)

print("Checking dev_fusion/linkedin-profile-scraper run history...")
try:
    runs = client.actor("dev_fusion/linkedin-profile-scraper").runs().list(limit=20, desc=True)
    print(f"Found {len(runs.items)} previous runs of dev_fusion actor:")
    for r in runs.items:
        print(" ", r["id"], r["status"], r.get("startedAt"))
    if len(runs.items) == 0:
        print(">>> NEVER USED. Full 10-run free trial should still be available.")
except Exception as e:
    print("Error checking dev_fusion:", e)
