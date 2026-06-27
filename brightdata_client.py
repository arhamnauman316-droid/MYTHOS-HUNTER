import os
import requests
import logging
import re
from datetime import datetime, timezone, date

logger = logging.getLogger(__name__)

SERP_KEY = os.getenv("SERP_API_KEY", "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0")

# Regex patterns that match relative date strings Google/LinkedIn surface in
# snippets, e.g. "3 days ago", "2w", "1 month ago", "5h", "yesterday".
_DATE_PATTERNS = [
    re.compile(r'\b(\d+)\s+(day|days|week|weeks|month|months|hour|hours)\s+ago\b', re.I),
    re.compile(r'\b(\d+)\s*([dwmh])\b'),
    re.compile(r'\byesterday\b', re.I),
    re.compile(r'\btoday\b', re.I),
]


def _serp(query: str, num: int = 5) -> list:
    """Search Google via SerpAPI and return organic results."""
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={"api_key": SERP_KEY, "engine": "google", "q": query, "num": num},
            timeout=45,
        )
        return resp.json().get("organic_results") or []
    except Exception as e:
        logger.warning(f"SerpAPI error: {e}")
        return []


def _extract_date_from_text(text: str) -> str:
    """
    Scan *text* for a recognisable relative-date expression and return it as a
    normalised string that ``parse_linkedin_date()`` in activity.py can handle.
    Returns an empty string when nothing is found.
    """
    if not text:
        return ""
    text_lower = text.lower()
    if re.search(r'\btoday\b', text_lower):
        return "today"
    if re.search(r'\byesterday\b', text_lower):
        return "yesterday"
    # "3 days ago", "2 weeks ago", "1 month ago", "5 hours ago"
    m = re.search(r'(\d+)\s+(hour|hours|day|days|week|weeks|month|months)\s+ago', text_lower)
    if m:
        value = m.group(1)
        unit = m.group(2).rstrip('s')[0]   # h / d / w / m
        return f"{value}{unit}"
    # Compact LinkedIn format: "2d", "3w", "1m", "5h"
    m = re.search(r'\b(\d+)\s*([dwmh])\b', text_lower)
    if m:
        return f"{m.group(1)}{m.group(2)}"
    return ""


def _search_linkedin_posts(name: str) -> list:
    """
    Run two targeted SerpAPI queries to find real LinkedIn posts or comments
    authored by *name*.  Returns a list of dicts with keys ``text`` and
    ``publishedAt``.  Falls back to an empty list when nothing useful is found.
    """
    queries = [
        f'"{name}" site:linkedin.com/posts',
        f'"{name}" site:linkedin.com/feed',
        f'"{name}" linkedin post',
    ]

    posts = []
    seen_snippets: set = set()

    for query in queries:
        if posts:
            # One good result is enough — avoid burning extra API quota.
            break
        results = _serp(query, num=5)
        for item in results:
            link = item.get("link", "")
            # Only keep results that look like LinkedIn post/activity pages.
            if not any(kw in link for kw in ("linkedin.com/posts", "linkedin.com/feed",
                                              "linkedin.com/in/", "linkedin.com/pulse")):
                continue

            snippet = (item.get("snippet") or "").strip()
            title   = (item.get("title")   or "").strip()

            if not snippet or len(snippet) < 20:
                continue

            # Deduplicate by the first 80 chars of the snippet.
            key = snippet[:80]
            if key in seen_snippets:
                continue
            seen_snippets.add(key)

            # Try to pull a date from the snippet first, then the title.
            published_at = _extract_date_from_text(snippet)
            if not published_at:
                published_at = _extract_date_from_text(title)
            # SerpAPI sometimes surfaces a structured "date" field.
            if not published_at:
                published_at = _extract_date_from_text(item.get("date", ""))
            if not published_at:
                published_at = "Recently"

            posts.append({"text": snippet[:300], "publishedAt": published_at})

    return posts


class BrightDataClient:

    def search_profiles(self, niche, limit=10):
        """Full pipeline: SerpAPI finds LinkedIn URLs + posts → profile list."""
        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        profiles = []
        seen = set()

        # Step 1: Find LinkedIn profile URLs via SerpAPI
        logger.info(f"SerpAPI search for niche: {niche}")
        results = _serp(f"{niche} linkedin profile site:linkedin.com/in", num=limit + 5)

        for item in results:
            link = item.get("link", "")
            if "linkedin.com/in/" not in link:
                continue
            parts = link.split("linkedin.com/in/")
            if len(parts) < 2:
                continue
            slug = parts[1].split("/")[0].split("?")[0].strip()
            if not slug or slug in seen or slug == "dir":
                continue
            seen.add(slug)

            url = f"https://www.linkedin.com/in/{slug}"
            title = item.get("title", "")
            snippet = item.get("snippet", "")

            # Parse name and headline from title
            name = ""
            headline = ""
            company = ""
            if " - " in title:
                parts2 = [p.strip() for p in title.split(" - ")]
                name = parts2[0]
                if len(parts2) > 1:
                    hl = parts2[1].replace("| LinkedIn", "").replace("LinkedIn", "").strip()
                    headline = hl
                    if " at " in hl.lower():
                        company = hl.split(" at ")[-1].strip()
            else:
                name = title.replace("| LinkedIn", "").strip()

            if not name or len(name) < 3:
                continue

            # Step 2: Search for real LinkedIn posts/comments by this person.
            logger.info(f"Searching for posts by: {name}")
            real_posts = _search_linkedin_posts(name)

            if real_posts:
                # Build the activity list from real post data so that
                # parse_linkedin_date() in activity.py gets a genuine date
                # string (e.g. "3d", "2 weeks ago") instead of a synthetic one.
                activity_list = [
                    {
                        "interaction": p["publishedAt"],
                        "title":       p["text"][:120],
                    }
                    for p in real_posts
                ]
                posts_list = real_posts
            else:
                # Fallback: no post results found via Google.  Use the profile
                # snippet as the post text and mark the date as "Unknown" so
                # the UI shows something meaningful rather than a fake "1d".
                logger.info(f"No post results found for {name}, using profile snippet as fallback")
                posts_list = [{"text": snippet[:200], "publishedAt": "Unknown"}]
                activity_list = [{"interaction": "Unknown", "title": snippet[:120]}]

            profiles.append({
                "fullName":    name,
                "linkedinUrl": url,
                "email":       "",
                "headline":    headline or snippet[:100],
                "about":       company,
                "posts":       posts_list,
                "activity":    activity_list,
                "status":      "Active",
                "scraped_at":  scraped_at,
            })

            if len(profiles) >= limit:
                break
        
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


def parse_profile_data(raw_record):
    """Convert profile format to what agent.py expects."""
    name   = raw_record.get("fullName") or raw_record.get("name") or ""
    posts  = raw_record.get("posts", [])

    # Prefer the activity list already built by search_profiles() which carries
    # real publishedAt values.  Only reconstruct it when it is absent (e.g. for
    # records that arrive from an external source without an activity field).
    activity = raw_record.get("activity") or []
    if not activity:
        for post in posts:
            text         = post.get("text", "")
            published_at = post.get("publishedAt") or "Unknown"
            activity.append({"interaction": published_at, "title": text[:120]})

    return {
        "name":            name,
        "Name":            name,
        "LinkedIn URL":    raw_record.get("linkedinUrl") or "",
        "Email":           raw_record.get("email") or "",
        "Headline":        raw_record.get("headline") or "",
        "Service Section": "",
        "About Section":   raw_record.get("about") or "",
        "Recent Activity": posts[0].get("text", "") if posts else "",
        "activity":        activity,
        "scraped_at":      raw_record.get("scraped_at") or "",
    }
