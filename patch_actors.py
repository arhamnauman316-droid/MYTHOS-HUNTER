path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

# Switch actors to data-slayer which works on free credits, no run limits
old1 = 'client.actor("harvestapi/linkedin-profile-scraper").call('
new1 = 'client.actor("data-slayer/linkedin-profile-scraper").call('

old2 = '"startUrls": start_urls,\n                    "findEmails": True,'
new2 = '"profileUrls": urls,'

old3 = 'client.actor("harvestapi/linkedin-profile-posts").call(\n                run_input={\n                    "startUrls": start_urls,\n                    "maxPostsPerProfile": 3,'
new3 = 'client.actor("data-slayer/linkedin-profile-posts-scraper").call(\n                run_input={\n                    "profileUrls": urls,\n                    "maxPostsPerProfile": 3,'

changes = 0
for old, new in [(old1, new1), (old2, new2), (old3, new3)]:
    if old in content:
        content = content.replace(old, new)
        changes += 1
        print(f"Replaced: {old[:50]}...")
    else:
        print(f"NOT FOUND: {old[:50]}...")

if changes > 0:
    open(path, "w", encoding="utf-8").write(content)
    print(f"\nDONE — {changes} changes applied")
