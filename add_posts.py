# Adds real post-fetching (harvestapi/linkedin-profile-posts) so activity
# status and message hooks use real data instead of guesses. Also dumps the
# raw posts response to debug_posts_raw.json so we can verify field names.
path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = """    def search_profiles(self, niche, limit=10):
        seed_urls = self.find_linkedin_urls(niche, 5)
        profiles = self.get_profiles_by_urls(seed_urls)
        if not profiles:
            logger.warning(f"No profiles from Apify for {niche}, using mock data")
            return self._mock_data(niche)
        return profiles"""

new = """    def get_posts_by_urls(self, urls):
        posts_by_url = {url: [] for url in urls}
        if not urls:
            return posts_by_url
        try:
            client = ApifyClient(self.apify_token)
            run = client.actor("harvestapi/linkedin-profile-posts").call(
                run_input={"urls": urls}
            )
            raw_posts = list(client.dataset(run["defaultDatasetId"]).iterate_items())

            import json as _json
            with open(r"C:\mythos-real\debug_posts_raw.json", "w", encoding="utf-8") as _f:
                _json.dump(raw_posts, _f, indent=2, default=str)
            logger.info(f"Posts actor returned {len(raw_posts)} items -> debug_posts_raw.json")

            for item in raw_posts:
                profile_url = (
                    item.get("profileUrl")
                    or item.get("authorProfileUrl")
                    or item.get("url")
                    or ""
                )
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
            return posts_by_url

    def search_profiles(self, niche, limit=10):
        seed_urls = self.find_linkedin_urls(niche, 5)
        profiles = self.get_profiles_by_urls(seed_urls)
        if not profiles:
            logger.warning(f"No profiles from Apify for {niche}, using mock data")
            return self._mock_data(niche)

        valid_urls = [p.get("linkedinUrl") or p.get("url") for p in profiles if (p.get("linkedinUrl") or p.get("url"))]
        posts_by_url = self.get_posts_by_urls(valid_urls)
        for p in profiles:
            u = p.get("linkedinUrl") or p.get("url")
            p["posts"] = posts_by_url.get(u, [])

        return profiles"""

if old not in content:
    print("ERROR: couldn't find the text to replace.")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Added get_posts_by_urls() and wired it into search_profiles()")
    print("This is a real second Apify actor call -> costs $5/1000 posts, separate from the $10/1k profile scrape")
