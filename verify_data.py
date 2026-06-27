import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient, parse_profile_data

bc = BrightDataClient()
profiles = bc.search_profiles("real estate coach", limit=3)

for p in profiles:
    parsed = parse_profile_data(p)
    print("=" * 50)
    print(f"Name:       {parsed.get('name')}")
    print(f"URL:        {parsed.get('url')}")
    print(f"Headline:   {parsed.get('headline')}")
    print(f"Company:    {parsed.get('about')}")
    print(f"Status:     {p.get('status')}")
    print(f"Last Post:  {p.get('Recent Activity','')[:120]}")
    print(f"Post Date:  {p.get('posts',[{}])[0].get('publishedAt','') if p.get('posts') else 'No post'}")
