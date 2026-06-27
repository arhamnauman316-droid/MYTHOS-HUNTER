import os
import requests
import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SERP_KEY = os.getenv("SERP_API_KEY", "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0")


def _serp(query: str, num: int = 5) -> list:
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


def _activity_id_to_date(url: str):
    """Decode LinkedIn activity ID to exact post datetime. 100% accurate."""
    match = re.search(r"activity-(\d+)", url)
    if not match:
        return None
    try:
        activity_id = int(match.group(1))
        timestamp_ms = activity_id >> 22
        timestamp_s = timestamp_ms / 1000
        return datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
    except Exception:
        return None


class BrightDataClient:

    def search_profiles(self, niche, limit=10):
        scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        profiles = []
        seen = set()

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

            # Step 2: Find posts via SerpAPI -> decode activity ID for exact date
            post_text = ""
            post_date = ""
            is_active = False
            try:
                now = datetime.now(timezone.utc)
                # Collect all posts from multiple queries
                all_post_results = []
                for q in [
                    f'linkedin.com/posts/{slug}',
                    f'"{name}" site:linkedin.com activity',
                ]:
                    all_post_results += _serp(q, num=10)

                # Find most recent post by decoding activity ID
                best_days = None
                for pr in all_post_results:
                    plink = pr.get("link", "")
                    psnippet = pr.get("snippet", "")
                    post_datetime = _activity_id_to_date(plink)
                    if post_datetime:
                        days_ago = (now - post_datetime).days
                        if best_days is None or days_ago < best_days:
                            best_days = days_ago
                            post_text = psnippet[:300]
                            post_date = post_datetime.strftime("%Y-%m-%d %H:%M UTC")
                            is_active = days_ago <= 14
                            if is_active:
                                post_date = "Posted in past 1-2 weeks"
                            elif days_ago < 30:
                                post_date = f"Last posted {days_ago} days ago"
                            elif days_ago < 365:
                                post_date = f"Last posted {days_ago // 30} month(s) ago"
                            else:
                                post_date = f"Last posted {days_ago // 365} year(s) ago"
                if best_days is not None:
                    logger.info(f"{name}: last post {best_days}d ago -> {'Active' if is_active else 'Inactive'}")
            except Exception as e:
                logger.warning(f"Post search failed for {name}: {e}")

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
    name = raw_record.get("name") or raw_record.get("fullName") or ""
    posts = raw_record.get("posts", [])
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
