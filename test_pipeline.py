import sys
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient
bc = BrightDataClient()
profiles = bc.search_profiles("fitness coach", limit=3)
for p in profiles:
    print(f"Name: {p['fullName']}")
    print(f"Email: {p['email']}")
    print(f"Post: {p['posts'][0]['text'][:80] if p['posts'] else 'No post'}")
    print(f"Status: {p['status']}")
    print("---")
