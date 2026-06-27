import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient, parse_profile_data
bc = BrightDataClient()
profiles = bc.search_profiles("fitness coach", limit=2)
for p in profiles:
    parsed = parse_profile_data(p)
    print(f"Name: {parsed.get('name')}")
    print(f"URL: {parsed.get('url')}")
    print(f"Status: {p.get('status')}")
    print(f"Post: {p.get('Recent Activity','')[:80]}")
    print("---")
