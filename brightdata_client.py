import os
import time
import requests
import logging
import re
from datetime import datetime, timezone, date

import config

logger = logging.getLogger(__name__)

SERP_KEY = os.getenv("SERP_API_KEY", "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0")

# Apify actor used to scrape LinkedIn profiles and their recent posts.
_APIFY_ACTOR_ID = "2SyF0bVxmgGr8IVCZ"  # apify/linkedin-profile-scraper
_APIFY_BASE_URL = "https://api.apify.com/v2"

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


def _get_linkedin_posts_via_apify(profile_url: str) -> list:
    """
    Scrape a LinkedIn profile via the Apify LinkedIn Profile Scraper actor and
    return the person's recent posts as a list of dicts with keys:
      - ``text``        – post body (str)
      - ``publishedAt`` – ISO-8601 date string or relative label (str)
      - ``likes``       – number of likes / reactions (int, may be 0)
      - ``comments``    – number of comments (int, may be 0)

    Returns an empty list when the token is absent, the actor run fails, or no
    posts are found in the response.
    """
    token = config.APIFY_TOKEN
    if not token:
        logger.warning("APIFY_TOKEN not configured – skipping Apify post fetch")
        return []

    headers = {"Content-Type": "application/json"}

    # ------------------------------------------------------------------ #
    # 1. Start the actor run                                               #
    # ------------------------------------------------------------------ #
    run_url = f"{_APIFY_BASE_URL}/acts/{_APIFY_ACTOR_ID}/runs"
    payload = {
        "profileUrls": [profile_url],
        "proxy": {"useApifyProxy": True},
    }
    try:
        run_resp = requests.post(
            run_url,
            json=payload,
            headers=headers,
            params={"token": token},
            timeout=30,
        )
        run_resp.raise_for_status()
        run_data = run_resp.json()
        run_id = run_data.get("data", {}).get("id")
        if not run_id:
            logger.warning(f"Apify: no run ID returned for {profile_url}")
            return []
    except Exception as e:
        logger.warning(f"Apify actor start failed for {profile_url}: {e}")
        return []

    logger.info(f"Apify run {run_id} started for {profile_url}")

    # ------------------------------------------------------------------ #
    # 2. Poll until the run finishes (max ~90 s)                          #
    # ------------------------------------------------------------------ #
    status_url = f"{_APIFY_BASE_URL}/actor-runs/{run_id}"
    terminal_statuses = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}
    for attempt in range(18):          # 18 × 5 s = 90 s ceiling
        time.sleep(5)
        try:
            status_resp = requests.get(
                status_url,
                params={"token": token},
                timeout=15,
            )
            status_resp.raise_for_status()
            run_status = status_resp.json().get("data", {}).get("status", "")
        except Exception as e:
            logger.warning(f"Apify status poll error (attempt {attempt + 1}): {e}")
            continue

        if run_status == "SUCCEEDED":
            break
        if run_status in terminal_statuses:
            logger.warning(f"Apify run {run_id} ended with status: {run_status}")
            return []

    else:
        logger.warning(f"Apify run {run_id} did not finish within timeout")
        return []

    # ------------------------------------------------------------------ #
    # 3. Fetch the dataset items                                           #
    # ------------------------------------------------------------------ #
    dataset_url = f"{_APIFY_BASE_URL}/actor-runs/{run_id}/dataset/items"
    try:
        items_resp = requests.get(
            dataset_url,
            params={"token": token, "format": "json"},
            timeout=30,
        )
        items_resp.raise_for_status()
        items = items_resp.json()
    except Exception as e:
        logger.warning(f"Apify dataset fetch failed for run {run_id}: {e}")
        return []

    if not items:
        logger.info(f"Apify returned no items for {profile_url}")
        return []

    # ------------------------------------------------------------------ #
    # 4. Extract posts from the first (and usually only) profile record   #
    # ------------------------------------------------------------------ #
    profile_record = items[0] if isinstance(items, list) else items
    raw_posts = (
        profile_record.get("posts")
        or profile_record.get("activity")
        or profile_record.get("recentActivity")
        or []
    )

    posts = []
    for raw in raw_posts:
        # Post body – try several common field names used by the actor.
        text = (
            raw.get("text")
            or raw.get("content")
            or raw.get("description")
            or raw.get("commentary")
            or ""
        ).strip()

        if not text or len(text) < 10:
            continue

        # Publication date – prefer an ISO timestamp, fall back to relative.
        published_at = (
            raw.get("publishedAt")
            or raw.get("postedAt")
            or raw.get("date")
            or raw.get("time")
            or "Unknown"
        )
        # Normalise epoch-millisecond timestamps to ISO strings.
        if isinstance(published_at, (int, float)) and published_at > 1_000_000_000:
            try:
                published_at = datetime.utcfromtimestamp(
                    published_at / 1000 if published_at > 1e12 else published_at
                ).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                published_at = "Unknown"

        # Engagement metrics (best-effort).
        likes    = raw.get("likes") or raw.get("reactions") or raw.get("numLikes") or 0
        comments = raw.get("comments") or raw.get("numComments") or 0

        posts.append({
            "text":        text[:500],
            "publishedAt": str(published_at),
            "likes":       int(likes) if str(likes).isdigit() else 0,
            "comments":    int(comments) if str(comments).isdigit() else 0,
        })

    logger.info(f"Apify returned {len(posts)} posts for {profile_url}")
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

            # Step 2: Fetch real LinkedIn posts via Apify's profile scraper.
            logger.info(f"Fetching Apify posts for: {url}")
            real_posts = _get_linkedin_posts_via_apify(url)

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
                logger.info(f"Apify returned no posts for {name}, using profile snippet as fallback")
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
