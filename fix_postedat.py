path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '                    "publishedAt": post.get("postedAt") or "",'
new = '                    "publishedAt": ((post.get("postedAt") or {}).get("postedAgoShort") or (post.get("postedAt") or {}).get("date") or ""),'

if old not in content:
    print("ERROR: not found")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
