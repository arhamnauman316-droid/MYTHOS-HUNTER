path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''    def find_linkedin_urls(self, niche, limit=5):
        """Search DuckDuckGo for real LinkedIn profiles matching any niche."""
        try:
            from duckduckgo_search import DDGS
            query = f'site:linkedin.com/in "{niche}"'
            results = []
            seen = set()
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=20):
                    url = r.get("href", "")
                    if "linkedin.com/in/" not in url:
                        continue
                    # Clean URL to just the profile base
                    parts = url.split("linkedin.com/in/")
                    if len(parts) < 2:
                        continue
                    slug = parts[1].split("/")[0].split("?")[0].strip()
                    if not slug or slug in seen:
                        continue
                    seen.add(slug)
                    clean_url = f"https://www.linkedin.com/in/{slug}"
                    results.append(clean_url)
                    if len(results) >= limit:
                        break
            if results:
                logger.info(f"DDG found {len(results)} LinkedIn URLs for niche: {niche}")
                return results
            logger.warning(f"DDG returned no LinkedIn URLs for niche: {niche}")
        except Exception as e:
            logger.error(f"DDG search error: {e}")
        # Fallback: empty list forces get_profiles_by_urls to use cached data
        return []'''

new = '''    def find_linkedin_urls(self, niche, limit=5):
        """Search DuckDuckGo for real LinkedIn profiles matching any niche."""
        try:
            from ddgs import DDGS
            queries = [
                f"{niche} linkedin profile",
                f"{niche} linkedin",
            ]
            seen = set()
            results = []
            with DDGS() as ddgs:
                for query in queries:
                    try:
                        for r in ddgs.text(query, max_results=20):
                            url = r.get("href", "")
                            if "linkedin.com/in/" not in url:
                                continue
                            parts = url.split("linkedin.com/in/")
                            if len(parts) < 2:
                                continue
                            slug = parts[1].split("/")[0].split("?")[0].strip()
                            if not slug or slug in seen or slug == "dir":
                                continue
                            seen.add(slug)
                            results.append(f"https://www.linkedin.com/in/{slug}")
                            if len(results) >= limit:
                                break
                    except Exception:
                        continue
                    if len(results) >= limit:
                        break
            if results:
                logger.info(f"DDG found {len(results)} LinkedIn URLs for niche: {niche}")
                return results
            logger.warning(f"DDG returned no LinkedIn URLs for niche: {niche}")
        except Exception as e:
            logger.error(f"DDG search error: {e}")
        return []'''

if old not in content:
    print("ERROR: not found")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
