path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''    def get_profiles_by_urls(self, urls):
        PROFILE_RUN_IDS = ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]
        POSTS_RUN_ID = "06YUVf8rv2NIY72BP"
        try:
            client = ApifyClient(self.apify_token)
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

            # Load posts and index by profile URL
            posts_by_url = {}
            posts_run_obj = client.run(POSTS_RUN_ID).get()
            posts_ds_id = posts_run_obj["defaultDatasetId"] if isinstance(posts_run_obj, dict) else posts_run_obj.default_dataset_id
            posts_items = list(client.dataset(posts_ds_id).iterate_items())
            for post in posts_items:
                q = post.get("query") or {}
                profile_url = (q.get("targetUrl") or "").rstrip("/")
                if not profile_url:
                    continue
                posts_by_url.setdefault(profile_url, []).append({
                    "text": (post.get("content") or "")[:120],
                    "publishedAt": ((post.get("postedAt") or {}).get("postedAgoShort") or (post.get("postedAt") or {}).get("date") or ""),
                })
            logger.info(f"Loaded posts for {len(posts_by_url)} profiles from posts run")

            # Load profiles and merge posts in
            seen_urls = set()
            valid_items = []
            skipped = 0
            for run_id in PROFILE_RUN_IDS:
                run_obj = client.run(run_id).get()
                dataset_id = run_obj["defaultDatasetId"] if isinstance(run_obj, dict) else run_obj.default_dataset_id
                items = list(client.dataset(dataset_id).iterate_items())
                for item in items:
                    if item.get("error") or item.get("status") in (404, 400, 403):
                        skipped += 1
                        continue
                    url = (item.get("linkedinUrl") or item.get("url") or "").rstrip("/")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    item["posts"] = posts_by_url.get(url, [])\n                    item["scraped_at"] = scraped_at
                    valid_items.append(item)
            logger.info(f"Apify (dual profile + posts): {len(valid_items)} unique valid profiles (read {scraped_at})")
            return valid_items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []'''

new = '''    def get_profiles_by_urls(self, urls):
        """Run Apify actors live with real URLs — profiles + emails + posts."""
        if not urls:
            logger.warning("No URLs to scrape")
            return []
        try:
            client = ApifyClient(self.apify_token)
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            start_urls = [{"url": u} for u in urls]

            # Step 1: Run profile scraper with email discovery
            logger.info(f"Running profile scraper for {len(urls)} URLs...")
            profile_run = client.actor("harvestapi/linkedin-profile-scraper").call(
                run_input={
                    "startUrls": start_urls,
                    "findEmails": True,
                }
            )
            profile_items = list(client.dataset(profile_run["defaultDatasetId"]).iterate_items())
            logger.info(f"Profile scraper returned {len(profile_items)} items")

            # Step 2: Run posts scraper
            logger.info(f"Running posts scraper for {len(urls)} URLs...")
            posts_run = client.actor("harvestapi/linkedin-profile-posts").call(
                run_input={
                    "startUrls": start_urls,
                    "maxPostsPerProfile": 3,
                }
            )
            posts_items = list(client.dataset(posts_run["defaultDatasetId"]).iterate_items())
            logger.info(f"Posts scraper returned {len(posts_items)} items")

            # Step 3: Index posts by profile URL
            posts_by_url = {}
            for post in posts_items:
                q = post.get("query") or {}
                profile_url = (q.get("targetUrl") or "").rstrip("/")
                if not profile_url:
                    profile_url = (post.get("authorUrl") or post.get("profileUrl") or "").rstrip("/")
                if not profile_url:
                    continue
                posts_by_url.setdefault(profile_url, []).append({
                    "text": (post.get("content") or post.get("text") or "")[:120],
                    "publishedAt": (
                        (post.get("postedAt") or {}).get("postedAgoShort") or
                        (post.get("postedAt") or {}).get("date") or
                        post.get("publishedAt") or ""
                    ),
                })
            logger.info(f"Indexed posts for {len(posts_by_url)} profiles")

            # Step 4: Merge posts into profiles
            seen_urls = set()
            valid_items = []
            for item in profile_items:
                if item.get("error") or item.get("status") in (404, 400, 403):
                    continue
                url = (item.get("linkedinUrl") or item.get("url") or "").rstrip("/")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                item["posts"] = posts_by_url.get(url, [])
                item["scraped_at"] = scraped_at
                valid_items.append(item)

            logger.info(f"Final: {len(valid_items)} valid profiles with posts merged")
            return valid_items
        except Exception as e:
            logger.error(f"Apify live run error: {e}")
            return []'''

if old not in content:
    idx = content.find("def get_profiles_by_urls")
    print(f"ERROR: old text not found exactly. Function found at index: {idx}")
    if idx >= 0:
        print("First 200 chars of actual function:")
        print(repr(content[idx:idx+200]))
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
