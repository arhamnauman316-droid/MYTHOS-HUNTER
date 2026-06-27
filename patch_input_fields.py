path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

# Fix profile scraper: use startUrls format (standard Apify) + restore start_urls var
old = '''            profile_run = client.actor("data-slayer/linkedin-profile-scraper").call(
                run_input={
                    "profileUrls": urls,
                }
            )'''

new = '''            start_urls = [{"url": u} for u in urls]
            profile_run = client.actor("data-slayer/linkedin-profile-scraper").call(
                run_input={
                    "startUrls": start_urls,
                }
            )'''

# Also fix posts scraper to use startUrls
old2 = '''            posts_run = client.actor("data-slayer/linkedin-profile-posts-scraper").call(
                run_input={
                    "profileUrls": urls,
                    "maxPostsPerProfile": 3,
                }
            )'''

new2 = '''            posts_run = client.actor("data-slayer/linkedin-profile-posts-scraper").call(
                run_input={
                    "startUrls": start_urls,
                    "maxPostsPerProfile": 3,
                }
            )'''

changes = 0
for o, n in [(old, new), (old2, new2)]:
    if o in content:
        content = content.replace(o, n)
        changes += 1
        print(f"Fixed: {o[:60]}...")
    else:
        print(f"NOT FOUND: {o[:60]}...")

if changes > 0:
    open(path, "w", encoding="utf-8").write(content)
    print(f"\nDONE — {changes} fixes applied")
