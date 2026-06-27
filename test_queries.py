import requests
KEY = "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0"

# Test different query formats for Mackenzie
queries = [
    'site:linkedin.com/posts/smithhmackenzie',
    '"smithhmackenzie" site:linkedin.com posts',
    '"Mackenzie S" site:linkedin.com activity',
    'linkedin.com/posts/smithhmackenzie',
]
for q in queries:
    r = requests.get("https://serpapi.com/search", params={
        "api_key": KEY, "engine": "google", "q": q, "num": 3
    }, timeout=30)
    results = r.json().get("organic_results", [])
    print(f"Query: {q}")
    print(f"Results: {len(results)}")
    for res in results:
        print(f"  Link: {res.get('link','')}")
    print("---")
