path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
old = '''                q = f\'site:linkedin.com/posts/{slug}\'
                post_results = _serp(q, num=5)'''
new = '''                q = f\'"{name}" site:linkedin.com activity\'
                post_results = _serp(q, num=5)'''
if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("FIXED")
else:
    print("NOT FOUND")
