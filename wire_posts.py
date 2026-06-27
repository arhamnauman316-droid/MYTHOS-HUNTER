path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''        RUN_IDS = ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]
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

new = '''        PROFILE_RUN_IDS = ["T3MpxFi5Umq9LGqNe", "PBxOnu9yhrhyZcfWD"]
        POSTS_RUN_ID = "06YUVf8rv2NIY72BP"
        try:
            client = ApifyClient(self.apify_token)
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

            # Load posts and index by profile URL
            posts_by_url = {}
            posts_run_info = client.run(POSTS_RUN_ID).get()
            posts_items = list(client.dataset(posts_run_info["defaultDatasetId"]).iterate_items())
            for post in posts_items:
                q = post.get("query") or {}
                profile_url = (q.get("targetUrl") or "").rstrip("/")
                if not profile_url:
                    continue
                posts_by_url.setdefault(profile_url, []).append({
                    "text": (post.get("content") or "")[:120],
                    "publishedAt": post.get("postedAt") or "",
                })
            logger.info(f"Loaded posts for {len(posts_by_url)} profiles from posts run")

            # Load profiles and merge posts in
            seen_urls = set()
            valid_items = []
            skipped = 0
            for run_id in PROFILE_RUN_IDS:
                run_info = client.run(run_id).get()
                dataset_id = run_info["defaultDatasetId"]
                items = list(client.dataset(dataset_id).iterate_items())
                for item in items:
                    if item.get("error") or item.get("status") in (404, 400, 403):
                        skipped += 1
                        continue
                    url = (item.get("linkedinUrl") or item.get("url") or "").rstrip("/")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    item["posts"] = posts_by_url.get(url, [])
                    item["scraped_at"] = scraped_at
                    valid_items.append(item)
            logger.info(f"Apify (dual profile + posts): {len(valid_items)} unique valid profiles (read {scraped_at})")
            return valid_items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []'''

if old not in content:
    print("ERROR: couldn't find old body")
    start = content.find("def get_profiles_by_urls")
    end = content.find("def expand_from_similar")
    print(repr(content[start:end]))
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE: posts wired in, profiles will now have real activity dates.")
