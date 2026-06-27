import requests
KEY = "AIzaSyCkge8PWzrA47oiEuQ7j7WazjxmXrcdAkU"
CX  = "a5e1f7d62c4b04efb"
q   = "Sergio Martinez linkedin post"
gr  = requests.get(
    "https://www.googleapis.com/customsearch/v1",
    params={"key": KEY, "cx": CX, "num": 3, "q": q},
    timeout=15,
)
data = gr.json()
items = data.get("items") or []
print(f"Total results: {len(items)}")
for item in items:
    print("Title:", item.get("title"))
    print("Snippet:", item.get("snippet","")[:150])
    print("---")
if not items:
    print("Raw:", str(data)[:500])
