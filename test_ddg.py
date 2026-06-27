import sys
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient
import config
bc = BrightDataClient()
urls = bc.find_linkedin_urls("fitness coach", limit=5)
print("Found URLs:")
for u in urls:
    print(" ", u)
