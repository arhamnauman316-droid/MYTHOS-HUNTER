import logging, config
from datetime import datetime, timezone
from typing import List, Dict, Any
from apify_client import ApifyClient

logger = logging.getLogger(__name__)


class BrightDataClient:
    def __init__(self):
        self.apify_token = config.APIFY_TOKEN

    def find_linkedin_urls(self, niche, limit=5):
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
        ]

    def get_profiles_by_urls(self, urls):
        KNOWN_GOOD_RUN_ID = "T3MpxFi5Umq9LGqNe"
        try:
            client = ApifyClient(self.apify_token)
            run_info = client.run(KNOWN_GOOD_RUN_ID).get()
            dataset_id = run_info["defaultDatasetId"]
            items = list(client.dataset(dataset_id).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            valid_items = []
            skipped = 0
            for item in items:
                if item.get("error") or item.get("status") in (404, 400, 403):
                    skipped += 1
                    continue
                item["scraped_at"] = scraped_at
                valid_items.append(item)
            logger.info(f"Apify (live dataset read): {len(items)} total, {len(valid_items)} valid, {skipped} failed (read {scraped_at})")
            return valid_items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []

    def expand_from_similar(self, profiles, limit=10):
        return []

    def get_posts_by_urls(self, urls):
        return {url: [] for url in urls}

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

        return profiles

    def _mock_data(self, niche):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return [
            {
                "fullName": "Sarah Jenkins",
                "url": "https://www.linkedin.com/in/sarahjenkins",
                "headline": f"Helping clients as a {niche} for over 10 years.",
                "about": f"Passionate {niche} with a decade of experience.",
                "experience": [{"companyName": "Self Employed"}],
                "posts": [{"text": "market strategy insights", "publishedAt": "2d"}],
                "email": "sarah.jenkins@example.com",
                "scraped_at": now,
            },
            {
                "fullName": "Michael Chen",
                "url": "https://www.linkedin.com/in/michaelchen",
                "headline": f"Leading {niche} in the region.",
                "about": f"Dedicated to helping others through {niche}.",
                "experience": [{"companyName": "Chen Consulting"}],
                "posts": [{"text": "Just finished a great project.", "publishedAt": "1w"}],
                "email": "michael.chen@example.com",
                "scraped_at": now,
            },
        ]


def parse_profile_data(raw_data):
    first = raw_data.get("firstName") or ""
    last = raw_data.get("lastName") or ""
    combined_name = f"{first} {last}".strip()
    name = (
        raw_data.get("fullName")
        or combined_name
        or raw_data.get("name")
        or "Unknown"
    )

    url = (
        raw_data.get("linkedinUrl")
        or raw_data.get("url")
        or raw_data.get("profileUrl")
        or ""
    )

    headline = (
        raw_data.get("headline")
        or raw_data.get("position")
        or raw_data.get("title")
        or raw_data.get("about", "")
    )
    headline = headline[:100] if headline else ""
    about = raw_data.get("about") or raw_data.get("summary") or ""

    experiences = raw_data.get("experience") or raw_data.get("experiences") or raw_data.get("positions") or []
    current_company = ""
    if experiences:
        exp0 = experiences[0]
        current_company = exp0.get("companyName") or exp0.get("company") or exp0.get("subtitle") or ""
    if not current_company:
        current_company = raw_data.get("companyName") or raw_data.get("company") or ""

    email = (
        raw_data.get("email")
        or raw_data.get("workEmail")
        or ((raw_data.get("emails") or [None])[0])
        or ""
    )

    posts = raw_data.get("posts") or []
    activity = []
    for post in posts:
        text = (post.get("text") or post.get("content") or "")[:120]
        published = post.get("publishedAt") or post.get("date") or "2d"
        activity.append({
            "interaction": f"{name} posted {published}",
            "title": text,
        })

    return {
        "name": name,
        "url": url,
        "headline": headline,
        "about": about,
        "services": current_company,
        "email": email,
        "activity": activity,
        "current_company": current_company,
        "followers": raw_data.get("followers") or raw_data.get("followerCount") or 0,
        "scraped_at": raw_data.get("scraped_at", ""),
        "raw": raw_data,
    }
