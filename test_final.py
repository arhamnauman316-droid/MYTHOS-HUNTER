import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient, parse_profile_data
bc = BrightDataClient()
profiles = bc.search_profiles("fitness coach", limit=3)
for p in profiles:
    print(f"Name:   {p['name']}")
    print(f"URL:    {p['url']}")
    print(f"Status: {p['status']}")
    print(f"Post:   {p.get('Recent Activity','')[:80]}")
    print(f"Date:   {p['posts'][0]['publishedAt'] if p['posts'] else 'No post'}")
    print("---")
