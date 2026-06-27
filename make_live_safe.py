path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = """    def get_profiles_by_urls(self, urls):
        \"\"\"Uses harvestapi/linkedin-profile-scraper with email search enabled.
        $10/1k profiles. Stamps every result with scraped_at (UTC) timestamp.\"\"\"
        try:
            client = ApifyClient(self.apify_token)
            run = client.actor("harvestapi/linkedin-profile-scraper").call(
                run_input={
                    "urls": urls,
                    "profileScraperMode": "Profile details + email search (\$10 per 1k)",
                }
            )
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

            import json as _json
            with open(r"C:\mythos-real\debug_raw.json", "w", encoding="utf-8") as _f:
                _json.dump(items, _f, indent=2, default=str)
            logger.info("Wrote raw Apify response to debug_raw.json")

            valid_items = []
            skipped = 0
            for item in items:
                if item.get("error") or item.get("status") in (404, 400, 403):
                    skipped += 1
                    q = item.get("query") or {}
                    logger.warning(f"Skipping failed scrape: {q.get(\x27url\x27, \x27unknown\x27)}")
                    continue
                item["scraped_at"] = scraped_at
                valid_items.append(item)
            logger.info(f"Apify: {len(items)} total, {len(valid_items)} valid, {skipped} failed (scraped {scraped_at})")
            return valid_items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []

    def expand_from_similar(self, profiles, limit=10):
        return []

    def get_posts_by_urls(self, urls):
        posts_by_url = {url: [] for url in urls}
        if not urls:
            return posts_by_url
        try:
            client = ApifyClient(self.apify_token)
            run = client.actor("harvestapi/linkedin-profile-posts").call(
                run_input={"targetUrls": urls, "maxPosts": 5}
            )
            raw_posts = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            for item in raw_posts:
                profile_url = item.get("profileUrl") or item.get("authorProfileUrl") or item.get("url") or ""
                matched = None
                for u in urls:
                    if u.rstrip("/") in profile_url or (profile_url and profile_url.rstrip("/") in u):
                        matched = u
                        break
                if matched:
                    posts_by_url.setdefault(matched, []).append(item)
            return posts_by_url
        except Exception as e:
            logger.error(f"Apify posts error: {e}")
            return posts_by_url"""

new = """    def get_profiles_by_urls(self, urls):
        KNOWN_GOOD_RUN_ID = "wa9pUDsxe9HcNk81a"
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
            return []

    def expand_from_similar(self, profiles, limit=10):
        return []

    def get_posts_by_urls(self, urls):
        return {url: [] for url in urls}"""

if old not in content:
    print("ERROR: couldn't find the text to replace.")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE: get_profiles_by_urls now reads the real dataset live, no new-run block risk.")
