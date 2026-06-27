import sys
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient

bc = BrightDataClient()

# Step 1: Find real URLs via DDG
print("Step 1: Finding LinkedIn URLs...")
urls = bc.find_linkedin_urls("fitness coach", limit=3)
for u in urls:
    print(" ", u)

# Step 2: Scrape them live via Apify
print("\nStep 2: Scraping profiles + posts + emails...")
profiles = bc.get_profiles_by_urls(urls)
print(f"Got {len(profiles)} profiles")

# Step 3: Show what we got
for p in profiles:
    print("\n---")
    print("Name:", p.get("fullName") or p.get("name"))
    print("Email:", p.get("email"))
    print("Posts:", len(p.get("posts", [])))
    if p.get("posts"):
        print("Last post:", p["posts"][0].get("publishedAt"))
