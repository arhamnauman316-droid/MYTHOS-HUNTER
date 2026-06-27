import sys
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient, parse_profile_data
bc = BrightDataClient()
profiles = bc.search_profiles("cybersecurity", limit=2)
for p in profiles:
    print("Raw:", p)
    try:
        result = parse_profile_data(p)
        print("OK:", result["name"])
    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()
