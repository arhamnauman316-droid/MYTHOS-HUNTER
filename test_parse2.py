import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient, parse_profile_data
bc = BrightDataClient()
profiles = bc.search_profiles("real estate coach", limit=2)
print(f"Got {len(profiles)} profiles")
for p in profiles:
    print("Keys:", list(p.keys()))
    try:
        r = parse_profile_data(p)
        print("OK:", r.get("name"))
    except Exception as e:
        import traceback
        traceback.print_exc()
