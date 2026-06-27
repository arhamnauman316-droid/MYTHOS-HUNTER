# Small in-place edit: just fixes get_profiles_by_urls to skip failed/404 scrapes
path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            for item in items:
                item["scraped_at"] = scraped_at
            logger.info(f"Apify returned {len(items)} profiles (scraped {scraped_at})")
            return items'''

new = '''            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            valid_items = []
            skipped = 0
            for item in items:
                if item.get("error") or item.get("status") in (404, 400, 403):
                    skipped += 1
                    q = item.get("query") or {}
                    logger.warning(f"Skipping failed scrape: {q.get('url', 'unknown')}")
                    continue
                item["scraped_at"] = scraped_at
                valid_items.append(item)
            logger.info(f"Apify: {len(items)} total, {len(valid_items)} valid, {skipped} failed (scraped {scraped_at})")
            return valid_items'''

if old not in content:
    print("ERROR: couldn't find the text to replace. File may already be edited or different.")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Fixed: get_profiles_by_urls now skips failed/404 scrapes")