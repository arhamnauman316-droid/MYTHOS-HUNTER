import os
import re
import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SERP_KEY = os.getenv("SERP_API_KEY", "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0")
ACTIVE_WINDOW_DAYS = 14  # Posted within 14 days = Active


def _serp(query: str, num: int = 10) -> list:
    """Search Google via SerpAPI."""
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


def _activity_id_to_days_ago(url: str) -> int | None:
    """Decode LinkedIn activity ID to exact days ago. 100% accurate."""
    match = re.search(r"activity-(\d+)", url)
    if not match:
        return None
    try:
        activity_id = int(match.group(1))
        timestamp_s = (activity_id >> 22) / 1000
        post_dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
        return (datetime.now(timezone.utc) - post_dt).days
    except Exception:
        return None


def _format_post_date(days_ago: int, is_active: bool) -> str:
    """Human readable post date."""
    if is_active:
        return "Posted in past 1-2 weeks"
    elif days_ago < 30:
        return f"Last posted {days_ago} days ago"
    elif days_ago < 365:
        months = days_ago // 30
        return f"Last posted {months} month{'s' if months > 1 else ''} ago"
    else:
        years = days_ago // 365
        return f"Last posted {years} year{'s' if years > 1 else ''} ago"


def _get_most_recent_post(name: str, slug: str) -> tuple[int | None, str, str]:
    """
    Search for most recent LinkedIn post.
    Returns (days_ago, post_text, post_date_str)
    """
    all_results = []

    # Query 1: direct slug search (most accurate)
    all_results += _serp(f"linkedin.com/posts/{slug}", num=10)

    # Query 2: name-based fallback
    all_results += _serp(f'"{name}" site:linkedin.com activity', num=10)

    best_days = None
    best_text = ""
    best_date_str = ""

    for r in all_results:
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        days = _activity_id_to_days_ago(link)
        if days is not None:
            if best_days is None or days < best_days:
                best_days = days
                best_text = snippet[:300]
                is_active = days <= ACTIVE_WINDOW_DAYS
                best_date_str = _format_post_date(days, is_active)

    return best_days, best_text, best_date_str


class BrightDataClient:

    def search_profiles(self, niche, limit=10):
        """
        Full pipeline:
        1. SerpAPI finds LinkedIn profile URLs for niche
        2. For each profile, find most recent post via activity ID
        3. Classify Active (posted within 14 days) or Inactive
        4. Return Active profiles first
        """
        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        profiles = []
        seen = set()

        logger.info(f"SerpAPI search for niche: {niche}")
        results = _serp(f"{niche} linkedin profile site:linkedin.com/in", num=limit + 5)

        for item in results:
            link = item.get("link", "")
            if "linkedin.com/in/" not in link:
                continue

            # Extract slug
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

            # Get most recent post
            days_ago, post_text, post_date = _get_most_recent_post(name, slug)

            is_active = days_ago is not None and days_ago <= ACTIVE_WINDOW_DAYS

            logger.info(
                f"{name}: {'posted ' + str(days_ago) + 'd ago' if days_ago is not None else 'no post found'} "
                f"-> {'Active' if is_active else 'Inactive'}"
            )

            profiles.append({
                "name":            name,
                "fullName":        name,
                "url":             url,
                "linkedinUrl":     url,
                "email":           "",
                "headline":        headline or snippet[:100],
                "services":        "",
                "about":           company,
                "Recent Activity": post_text,
                "posts": [{"text": post_text, "publishedAt": post_date}] if post_text else [],
                "status":          "Active" if is_active else "Inactive",
                "scraped_at":      scraped_at,
            })

            if len(profiles) >= limit:
                break

        # Sort: Active profiles first
        profiles.sort(key=lambda x: x["status"] != "Active")

        active = len([p for p in profiles if p["status"] == "Active"])
        logger.info(f"Pipeline complete: {len(profiles)} profiles ({active} Active)")
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
    name   = raw_record.get("name") or raw_record.get("fullName") or ""
    posts  = raw_record.get("posts", [])
    status = raw_record.get("status", "Inactive")

    activity = []
    for post in posts:
        text = post.get("text", "")
        interaction = "1d" if status == "Active" else "60d"
        activity.append({"interaction": interaction, "title": text[:120]})

    if status == "Active" and not activity:
        activity = [{"interaction": "1d", "title": ""}]

    return {
        "name":            name,
        "Name":            name,
        "url":             raw_record.get("url") or raw_record.get("linkedinUrl") or "",
        "LinkedIn URL":    raw_record.get("url") or raw_record.get("linkedinUrl") or "",
        "email":           raw_record.get("email") or "",
        "Email":           raw_record.get("email") or "",
        "headline":        raw_record.get("headline") or "",
        "Headline":        raw_record.get("headline") or "",
        "services":        "",
        "Service Section": "",
        "about":           raw_record.get("about") or "",
        "About Section":   raw_record.get("about") or "",
        "Recent Activity": raw_record.get("Recent Activity") or (posts[0].get("text", "") if posts else ""),
        "activity":        activity,
        "scraped_at":      raw_record.get("scraped_at") or "",
    }
