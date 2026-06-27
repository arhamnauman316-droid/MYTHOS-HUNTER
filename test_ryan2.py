import sys, logging
logging.basicConfig(level=logging.INFO)
sys.path.insert(0, r"C:\mythos-real")
from brightdata_client import BrightDataClient

bc = BrightDataClient()

# Manually test Ryan Serhant
import requests, re
from datetime import datetime, timezone
KEY = "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0"

def activity_id_to_date(url):
    match = re.search(r"activity-(\d+)", url)
    if not match: return None
    try:
        return datetime.fromtimestamp((int(match.group(1)) >> 22) / 1000, tz=timezone.utc)
    except: return None

now = datetime.now(timezone.utc)
for q in ["linkedin.com/posts/ryanserhant", '"Ryan Serhant" site:linkedin.com activity']:
    r = requests.get("https://serpapi.com/search", params={
        "api_key": KEY, "engine": "google", "q": q, "num": 5
    }, timeout=30)
    results = r.json().get("organic_results", [])
    print(f"\nQuery: {q} → {len(results)} results")
    for res in results[:3]:
        link = res.get("link","")
        d = activity_id_to_date(link)
        days = (now-d).days if d else None
        print(f"  {link[:70]}")
        print(f"  Days ago: {days}")
