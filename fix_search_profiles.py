path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''        valid_urls = [p.get("linkedinUrl") or p.get("url") for p in profiles if (p.get("linkedinUrl") or p.get("url"))]
        posts_by_url = self.get_posts_by_urls(valid_urls)
        for p in profiles:
            u = p.get("linkedinUrl") or p.get("url")
            p["posts"] = posts_by_url.get(u, [])

        return profiles'''

new = '''        # Posts already merged into profiles by get_profiles_by_urls
        return profiles'''

if old not in content:
    print("ERROR: not found")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
