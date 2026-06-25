import os
import requests
import logging
import re
from datetime import datetime, timezone, date

logger = logging.getLogger(__name__)

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCkge8PWzrA47oiEuQ7j7WazjxmXrcdAkU")
GOOGLE_CX = os.getenv("GOOGLE_CX", "a5e1f7d62c4b04efb")


class BrightDataClient:

    def search_profiles(self, niche, limit=10):
        """Full pipeline: DFG search → Google post → profile list."""
        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        profiles = []

        # Step 1: DFG search for LinkedIn profiles
        logger.info(f"DD search for niche: {niche}")
        try:
            from ddgs import DDGS
            results = []
            seen = set()
            with DDGS() as ddgs:
                for r in ddgs.text(f"{niche} linkedin profile", max_results=30):
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
                    results.append({
                        "url": f"https://www.linkedin.com/in/{slug}",
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                    })
                    if len(results) >= limit:
                        break
            logger.info(f"DD found {len(results)} profiles")
        except Exception as e:
            logger.error(f"DD search error: {e}")
            results = []

        if not results:
            return []

        # Step 2: Parse name/headline from DG results + Google post
        for r in results:
            title = r.get("title", "")
            body  = r.get("body", "")
            url   = r.get("url", "")

            # Parse name from title: "First Last - Title | LinkedIn"
            name = ""
            headline = ""
            company = ""
            if " - " in title:
                parts = [p.strip() for p in title.split(" - ")]
                name = parts[0]
                if len(parts) > 1:
                    hl = parts[1].replace("| LinkedIn", "").replace("LinkedIn", "").strip()
                    if " at " in hl.lower():
                        headline = hl
                        company = hl.split(" at ", 1)[-1].strip()
                    elif len(parts) > 2:
                        headline = hl
                        company = parts[2].replace("| LinkedIn", "").strip()
                    else:
                        headline = hl
            else:
                name = title.replace("| LinkedIn", "").strip()

            if not name:
                continue

            # Google search for latest LinkedIn post
            post_text = ""
            post_date = ""
            is_active = False
            try:
                from ddgs import DDGS
                q = f"{name} {company} linkedin post".strip()
                with DDGS() as ddgs:
                    presults = list(ddgs.text(q, max_results=3))
                for pr in presults:
                    plink = pr.get("href", "")
                    if "linkedin.com" in plink:
                        post_text = pr.get("body", "")[:200]
                        post_date = "Recently"
                        is_active = True
                        break
                else:
                    if presults:
                        post_text = presults[0].get("body", "")[:200]
                        post_date = "Recently"
                        is_active = True
            except Exception as e:
                logger.warning(f"DDG post search failed for {name}: {e}")

            profiles.append({
                "fullName": name,
                "linkedinUrl": url,
                "email": "",
                "headline": headline or body[:100],
                "about": company,
                "posts": [{"text": post_text, "publishedAt": post_date}] if post_text else [],
                "status": "Active" if is_active else "Inactive",
                "scraped_at": scraped_at,
            })

        logger.info(f"Pipeline complete: {len(profiles)} profiles")
        return profiles

    def get_profiles_by_urls(self, urls):
        return []

    def find_linkedin_urls(self, niche, limit=5):
        return []

    def expand_from_similar(self, profiles, limit=10):
        return []

    def get_posts_by_urls(self, urls):
        return {url: [] for url in urls}
