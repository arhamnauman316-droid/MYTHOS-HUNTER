path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
old = '''                q = f\'"{name}" site:linkedin.com activity\'
                post_results = _serp(q, num=5)'''
new = '''                # Use slug for exact match, fall back to name
                q = f\'linkedin.com/posts/{slug}\'
                post_results = _serp(q, num=5)
                # If no results with slug, try name
                if not post_results:
                    q = f\'"{name}" site:linkedin.com activity\'
                    post_results = _serp(q, num=5)'''
if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("FIXED")
else:
    print("NOT FOUND")
