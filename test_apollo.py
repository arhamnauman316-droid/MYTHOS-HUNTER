import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient
bc = BrightDataClient()
print("Testing Apollo...")
import requests
resp = requests.post(
    "https://api.apollo.io/api/v1/mixed_people/search",
    headers={"Content-Type": "application/json"},
    json={"api_key": "O_w6vzp6Jw6vdzBa8W5k1g", "person_titles": ["fitness coach"], "per_page": 3, "page": 1},
    timeout=30,
)
print("Status:", resp.status_code)
print("Response:", resp.text[:500])
