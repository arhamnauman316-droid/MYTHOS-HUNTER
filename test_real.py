import sys
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient
bc = BrightDataClient()
profiles = bc.search_profiles("real estate coach", limit=3)
for p in profiles:
    print(f"Name: {p['fullName']}")
    print(f"URL: {p['linkedinUrl']}")
    print(f"Headline: {p['headline']}")
    print(f"Post: {p['posts'][0]['text'][:100] if p['posts'] else 'No post'}")
    print("---")
