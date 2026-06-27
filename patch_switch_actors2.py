path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

# Switch profile scraper to dev_fusion (known working, different developer)
old1 = '''            profile_run = client.actor("data-slayer/linkedin-profile-scraper").call(
                run_input={
                    "startUrls": start_urls,
                }
            )'''
new1 = '''            profile_run = client.actor("dev_fusion/linkedin-profile-scraper").call(
                run_input={
                    "profileUrls": [u for u in urls],
                    "findEmails": True,
                }
            )'''

# Switch posts back to harvestapi (different actor, no run limit issue)
old2 = '''            posts_run = client.actor("data-slayer/linkedin-profile-posts-scraper").call(
                run_input={
                    "startUrls": start_urls,
                    "maxPostsPerProfile": 3,
                }
            )'''
new2 = '''            posts_run = client.actor("harvestapi/linkedin-profile-posts").call(
                run_input={
                    "startUrls": start_urls,
                    "maxPostsPerProfile": 3,
                }
            )'''

changes = 0
for o, n in [(old1, new1), (old2, new2)]:
    if o in content:
        content = content.replace(o, n)
        changes += 1
        print(f"Fixed: {o[:60]}...")
    else:
        print(f"NOT FOUND: {o[:60]}...")

if changes > 0:
    open(path, "w", encoding="utf-8").write(content)
    print(f"\nDONE — {changes} changes applied")
