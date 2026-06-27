path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = '''    def find_linkedin_urls(self, niche, limit=5):
        niche_seeds = {
            "real estate coach": [
                "https://www.linkedin.com/in/tomferry/",
                "https://www.linkedin.com/in/mikeferry/",
                "https://www.linkedin.com/in/beverly-steiner-9b5b5b1/",
                "https://www.linkedin.com/in/darryl-davis-1234/",
                "https://www.linkedin.com/in/brian-buffini/",
            ],
            "business consultant": [
                "https://www.linkedin.com/in/simon-sinek/",
                "https://www.linkedin.com/in/garyvaynerchuk/",
                "https://www.linkedin.com/in/reidhoffman/",
                "https://www.linkedin.com/in/jeffweiner08/",
                "https://www.linkedin.com/in/melissaambrosini/",
            ],
            "life coach": [
                "https://www.linkedin.com/in/tonyrobbins/",
                "https://www.linkedin.com/in/brendonburchard/",
                "https://www.linkedin.com/in/marie-forleo/",
                "https://www.linkedin.com/in/robbinsresearch/",
                "https://www.linkedin.com/in/jackcanfield/",
            ],
            "marketing coach": [
                "https://www.linkedin.com/in/neilpatel/",
                "https://www.linkedin.com/in/jaybaer/",
                "https://www.linkedin.com/in/annhandley/",
                "https://www.linkedin.com/in/joepulizzi/",
                "https://www.linkedin.com/in/sethjgodin/",
            ],
        }
        niche_lower = niche.lower().strip()
        for key in niche_seeds:
            if key in niche_lower or niche_lower in key:
                urls = niche_seeds[key][:limit]
                logger.info(f"Using {len(urls)} seed URLs for niche: {niche}")
                return urls
        logger.info("No seeds for niche, using defaults")
        return [
            "https://www.linkedin.com/in/elad-moshe-05a90413/",
            "https://www.linkedin.com/in/jonathan-myrvik-3baa01109/",
        ]'''

new = '''    def find_linkedin_urls(self, niche, limit=5):
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

if old not in content:
    print("ERROR: old text not found")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
