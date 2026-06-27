import json

with open(r"C:\mythos-real\debug_raw.json", "r", encoding="utf-8") as f:
    items = json.load(f)

for i, item in enumerate(items):
    if item.get("error"):
        print(f"--- Item {i+1}: FAILED ({item.get('error')}) ---")
        continue

    print(f"--- Item {i+1}: SUCCESS ---")
    print("Top-level keys:", list(item.keys()))
    print()

    for k in item.keys():
        if "email" in k.lower() or "mail" in k.lower():
            print(f"  EMAIL FIELD '{k}':", item[k])

    for k in item.keys():
        if "post" in k.lower() or "activit" in k.lower() or "update" in k.lower():
            val = item[k]
            print(f"  ACTIVITY FIELD '{k}':", json.dumps(val, indent=2)[:1000])

    print()
    print("=" * 60)
    print()
