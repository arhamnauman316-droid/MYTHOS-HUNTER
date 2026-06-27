path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '        KNOWN_GOOD_RUN_ID = "T3MpxFi5Umq9LGqNe"'

new = '''        RUN_IDS = ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]'''

# Also need to replace the body that uses KNOWN_GOOD_RUN_ID
old_body = '''        KNOWN_GOOD_RUN_ID = "T3MpxFi5Umq9LGqNe"
        try:
            client = ApifyClient(self.apify_token)
            run_info = client.run(KNOWN_GOOD_RUN_ID).get()
            dataset_id = run_info["defaultDatasetId"]
            items = list(client.dataset(dataset_id).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            valid_items = []
            skipped = 0
            for item in items:
                if item.get("error") or item.get("status") in (404, 400, 403):
                    skipped += 1
                    continue
                item["scraped_at"] = scraped_at
                valid_items.append(item)
            logger.info(f"Apify (live dataset read): {len(items)} total, {len(valid_items)} valid, {skipped} failed (read {scraped_at})")
            return valid_items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []'''

new_body = '''        RUN_IDS = ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]
        try:
            client = ApifyClient(self.apify_token)
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            seen_urls = set()
            valid_items = []
            skipped = 0
            for run_id in RUN_IDS:
                run_info = client.run(run_id).get()
                dataset_id = run_info["defaultDatasetId"]
                items = list(client.dataset(dataset_id).iterate_items())
                for item in items:
                    if item.get("error") or item.get("status") in (404, 400, 403):
                        skipped += 1
                        continue
                    url = item.get("linkedinUrl") or item.get("url") or ""
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    item["scraped_at"] = scraped_at
                    valid_items.append(item)
            logger.info(f"Apify (dual dataset read): {len(valid_items)} unique valid profiles (read {scraped_at})")
            return valid_items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []'''

if old_body not in content:
    print("ERROR: couldn't find old body text")
    # show current get_profiles_by_urls for debugging
    start = content.find("def get_profiles_by_urls")
    end = content.find("def expand_from_similar")
    print(repr(content[start:end]))
else:
    content = content.replace(old_body, new_body)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE: now reads from both run IDs, deduped.")
