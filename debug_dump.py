# One-time debug: dumps raw Apify items to a JSON file so we can see
# the real field names for posts/activity dates and email, instead of guessing.
path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            valid_items = []'''

new = '''            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

            import json as _json
            with open(r"C:\\mythos-real\\debug_raw.json", "w", encoding="utf-8") as _f:
                _json.dump(items, _f, indent=2, default=str)
            logger.info("Wrote raw Apify response to debug_raw.json")

            valid_items = []'''

if old not in content:
    print("ERROR: couldn't find the text to replace. Check if fix_filter.py was applied already.")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Added debug dump -> debug_raw.json will be written on next run")