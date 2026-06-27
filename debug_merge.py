import sys
sys.path.insert(0, r"C:\mythos-real")
import config
from apify_client import ApifyClient
from brightdata_client import parse_profile_data

client = ApifyClient(config.APIFY_TOKEN)

# Load posts
posts_by_url = {}
posts_run = client.run("06YUVf8rv2NIY72BP").get()
posts_items = list(client.dataset(posts_run["defaultDatasetId"]).iterate_items())
for post in posts_items:
    q = post.get("query") or {}
    url = (q.get("targetUrl") or "").rstrip("/")
    posts_by_url.setdefault(url, []).append(post)

print("Posts indexed under URLs:")
for u in posts_by_url:
    print(f"  {u!r} -> {len(posts_by_url[u])} posts")

# Load profiles
print("\nProfile URLs:")
for run_id in ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]:
    run_info = client.run(run_id).get()
    items = list(client.dataset(run_info["defaultDatasetId"]).iterate_items())
    for item in items:
        if item.get("error"): continue
        url = (item.get("linkedinUrl") or item.get("url") or "").rstrip("/")
        matched = posts_by_url.get(url, [])
        print(f"  {url!r} -> matched {len(matched)} posts")
