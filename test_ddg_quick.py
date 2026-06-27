from ddgs import DDGS
with DDGS() as d:
    results = list(d.text("cybersecurity linkedin profile", max_results=5))
    for r in results:
        print(r.get("href",""))
