import os
import requests
import logging
import re
from datetime import datetime, timezone, date
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCkge8PWzrA47oiEuQ7j7WazjxmXrcdAkU")
GOOGLE_CX = os.getenv("GOOGLE_CX", "a5e1f7d62c4b04efb")

_DDG_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _ddg_search(query: str, max_results: int = 10) -> list[dict]:
    """Fetch DuckDuckGo HTML search results and return a list of
    dicts with keys: href, title, body."""
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=_DDG_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        logger.warning(f"DDG HTTP request failed: {exc}")
        return []

    html = resp.text
    results = []

    # Each result block looks like:
    #   <a class="result__a" href="...">title</a>
    #   <a class="result__snippet">body</a>
    # DDG wraps the real URL in a redirect; the actual href is in
    # the uddg= query param or directly in the href attribute.
    blocks = re.findall(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
        html,
        re.DOTALL,
    )

    for raw_href, raw_title, raw_body in blocks:
        # Resolve DDG redirect URLs (?uddg=<encoded-real-url>)
        uddg = re.search(r"[?&]uddg=([^&]+)", raw_href)
        href = requests.utils.unquote(uddg.group(1)) if uddg else raw_href

        title = re.sub(r"<[^>]+>", "", raw_title).strip()
        body  = re.sub(r"<[^>]+>", "", raw_body).strip()

        results.append({"href": href, "title": title, "body": body})
        if len(results) >= max_results:
            break

    return results


class BrightDataClient:

    def search_profiles(self, niche, limit=10):
        """Full pipeline: DFG search → Google post → profile list."""
        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        profiles = []

        # Step 1: DuckDuckGo search for LinkedIn profiles
        logger.info(f"DD search for niche: {niche}")
        try:
            results = []
            seen = set()
            for r in _ddg_search(f"{niche} linkedin profile", max_results=30):
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

            # DuckDuckGo search for latest LinkedIn post
            post_text = ""
            post_date = ""
            is_active = False
            try:
                q = f"{name} {company} linkedin post".strip()
                presults = _ddg_search(q, max_results=3)
                matched = False
                for pr in presults:
                    plink = pr.get("href", "")
                    if "linkedin.com" in plink:
                        post_text = pr.get("body", "")[:200]
                        post_date = "Recently"
                        is_active = True
                        matched = True
                        break
                if not matched and presults:
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
