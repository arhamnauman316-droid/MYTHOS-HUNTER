path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
content = content.replace("is_active = days_ago <= 7", "is_active = days_ago <= 25")
content = content.replace("is_active = days_ago <= 30", "is_active = days_ago <= 25")
content = content.replace("Within 7 days", "Within 25 days")
content = content.replace("Within 30 days", "Within 25 days")
open(path, "w", encoding="utf-8").write(content)
print("DONE")
