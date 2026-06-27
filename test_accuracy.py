import requests, re
from datetime import datetime, timezone

KEY = "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0"

def get_days(url):
    m = re.search(r"activity-(\d+)", url)
    if not m: return None
    try: return (datetime.now(timezone.utc) - datetime.fromtimestamp((int(m.group(1))>>22)/1000, tz=timezone.utc)).days
    except: return None

slug = "james-houghtaling-4a9956118"
name = "James Houghtaling"

# Try with higher limit - get most recent post
r = requests.get("https://serpapi.com/search", params={
    "api_key": KEY, "engine": "google",
    "q": f'linkedin.com/posts/{slug}',
    "num": 10
}, timeout=30).json()

results = r.get("organic_results", [])
print(f"Results: {len(results)}")
# Find the most recent post (smallest days_ago)
posts = []
for res in results:
    link = res.get("link","")
    days = get_days(link)
    if days is not None:
        posts.append((days, link, res.get("snippet","")[:80]))

posts.sort()  # Sort by most recent first
for days, link, snippet in posts:
    print(f"{days}d ago | {link[:60]}")
    print(f"  {snippet}")
