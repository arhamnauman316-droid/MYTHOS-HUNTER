import sys
sys.path.insert(0, r"C:\mythos-real")
import config
from apify_client import ApifyClient
from brightdata_client import parse_profile_data
from agent import extract_date_from_interaction
from activity import parse_linkedin_date, classify_profile

client = ApifyClient(config.APIFY_TOKEN)

posts_by_url = {}
posts_run = client.run("06YUVf8rv2NIY72BP").get()
for post in client.dataset(posts_run["defaultDatasetId"]).iterate_items():
    q = post.get("query") or {}
    url = (q.get("targetUrl") or "").rstrip("/")
    posts_by_url.setdefault(url, []).append(post)

run_info = client.run("T3MpxFi5Umq9LGqNe").get()
items = list(client.dataset(run_info["defaultDatasetId"]).iterate_items())
for item in items:
    if item.get("error"): continue
    url = (item.get("linkedinUrl") or "").rstrip("/")
    item["posts"] = posts_by_url.get(url, [])
    profile = parse_profile_data(item)
    print(f"\n=== {profile['name']} ===")
    print(f"  posts in raw: {len(item['posts'])}")
    print(f"  activity built: {len(profile['activity'])}")
    if profile["activity"]:
        act = profile["activity"][0]
        print(f"  interaction: {act['interaction']!r}")
        date_str = extract_date_from_interaction(act["interaction"])
        print(f"  date_str: {date_str!r}")
        if date_str:
            d = parse_linkedin_date(date_str)
            print(f"  parsed date: {d}")
            print(f"  classify: {classify_profile(d, 30)}")
