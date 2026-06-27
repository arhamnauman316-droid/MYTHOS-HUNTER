import sys, logging, requests
logging.basicConfig(level=logging.INFO)

KEY = "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0"

# Test what SerpAPI actually returns for her posts
resp = requests.get("https://serpapi.com/search", params={
    "api_key": KEY, "engine": "google", "num": 3,
    "q": '"Mackenzie S" site:linkedin.com post'
}, timeout=30)

for r in resp.json().get("organic_results", []):
    print("Link:", r.get("link"))
    print("Date:", r.get("date"))
    print("Snippet:", r.get("snippet","")[:150])
    print("---")
