# Fixes the posts actor input field: it's "targetUrls", not "urls" --
# that's why it ran successfully but returned 0 items.
path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = """            run = client.actor("harvestapi/linkedin-profile-posts").call(
                run_input={"urls": urls}
            )"""

new = """            run = client.actor("harvestapi/linkedin-profile-posts").call(
                run_input={"targetUrls": urls, "maxPosts": 5}
            )"""

if old not in content:
    print("ERROR: couldn't find the text to replace.")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Fixed: posts actor now uses targetUrls (was urls) + maxPosts=5")
