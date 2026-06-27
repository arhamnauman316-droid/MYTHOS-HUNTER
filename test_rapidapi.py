import requests, json, os
from dotenv import load_dotenv
load_dotenv(r"C:\mythos-real\.env")

KEY = os.getenv("RAPIDAPI_KEY")
HOST = "linkedin-data-api.p.rapidapi.com"
HEADERS = {"x-rapidapi-host": HOST, "x-rapidapi-key": KEY}

# Test 1: Search People by niche
print("=== SEARCH PEOPLE ===")
r = requests.get(f"https://{HOST}/search-people", headers=HEADERS, params={"keywords": "fitness coach", "start": 0})
print(json.dumps(r.json(), indent=2)[:2000])
