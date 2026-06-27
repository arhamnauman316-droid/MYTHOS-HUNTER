import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient, parse_profile_data
import agent

bc = BrightDataClient()
profiles = bc.search_profiles("fitness coach", limit=2)
for p in profiles:
    result = agent.process_lead(p)
    if result:
        print("url:", result.get("url"))
        print("LinkedIn URL:", result.get("LinkedIn URL"))
        print("Recent Activity:", result.get("Recent Activity","")[:80])
        print("Status:", result.get("Status"))
        print("---")
