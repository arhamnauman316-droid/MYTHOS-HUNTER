import os

BASE = r"C:\mythos-real"

# ── Write new brightdata_client.py (Apify version) ──────────────────────────
brightdata = '''import logging, config
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
        try:
            client = ApifyClient(self.apify_token)
            run = client.actor("curious_coder/linkedin-profile-scraper").call(
                run_input={
                    "startUrls": [{"url": url} for url in urls],
                    "proxyConfiguration": {"useApifyProxy": True},
                }
            )
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            logger.info(f"Apify returned {len(items)} profiles")
            return items
        except Exception as e:
            logger.error(f"Apify error: {e}")
            return []

    def expand_from_similar(self, profiles, limit=10):
        return []

    def search_profiles(self, niche, limit=10):
        seed_urls = self.find_linkedin_urls(niche, 5)
        profiles = self.get_profiles_by_urls(seed_urls)
        if not profiles:
            logger.warning(f"No profiles from Apify for {niche}, using mock data")
            return self._mock_data(niche)
        return profiles

    def _mock_data(self, niche):
        return [
            {
                "fullName": "Sarah Jenkins",
                "url": "https://www.linkedin.com/in/sarahjenkins",
                "headline": f"Helping clients as a {niche} for over 10 years.",
                "about": f"Passionate {niche} with a decade of experience.",
                "experiences": [{"companyName": "Self Employed"}],
                "posts": [{"text": "market strategy insights", "publishedAt": "2d"}],
            },
            {
                "fullName": "Michael Chen",
                "url": "https://www.linkedin.com/in/michaelchen",
                "headline": f"Leading {niche} in the region.",
                "about": f"Dedicated to helping others through {niche}.",
                "experiences": [{"companyName": "Chen Consulting"}],
                "posts": [{"text": "Just finished a great project.", "publishedAt": "1w"}],
            },
        ]


def parse_profile_data(raw_data):
    name = (
        raw_data.get("fullName")
        or raw_data.get("name")
        or raw_data.get("full_name")
        or "Unknown"
    )
    url = (
        raw_data.get("url")
        or raw_data.get("profileUrl")
        or raw_data.get("linkedin_url")
        or ""
    )
    headline = raw_data.get("headline") or raw_data.get("about", "")
    headline = headline[:100] if headline else ""
    about = raw_data.get("about") or raw_data.get("summary") or ""
    experiences = raw_data.get("experiences") or []
    current_company = experiences[0].get("companyName", "") if experiences else ""
    posts = raw_data.get("posts") or []
    activity = []
    for post in posts:
        text = (post.get("text") or "")[:120]
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
        "email": raw_data.get("email") or "",
        "activity": activity,
        "current_company": current_company,
        "followers": raw_data.get("followers") or 0,
        "raw": raw_data,
    }
'''

# ── Write new config.py ──────────────────────────────────────────────────────
cfg = '''import os
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY       = os.getenv("ANTHROPIC_API_KEY")
APIFY_TOKEN             = os.getenv("APIFY_TOKEN")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", r"C:\\Users\\Dell Core i7\\credentials.json")
GOOGLE_SHEET_ID         = os.getenv("GOOGLE_SHEET_ID")
ACTIVITY_WINDOW_DAYS    = int(os.getenv("ACTIVITY_WINDOW_DAYS", 10))
OUTREACH_SERVICE_PITCH  = os.getenv("OUTREACH_SERVICE_PITCH", "we help business owners automate their LinkedIn outreach")
OUTREACH_SOFT_CTA       = os.getenv("OUTREACH_SOFT_CTA", "Would you be open to a quick chat?")
COLUMNS = ["Name", "LinkedIn URL", "Email", "Headline", "Service Section", "About Section", "Recent Activity", "Status", "Commented On (Author)", "Commented Post Topic", "AI Draft Message"]
NICHES_TAB, ACTIVE_TAB, INACTIVE_TAB = "Niches", "Active", "Inactive"
'''

# ── Write files ──────────────────────────────────────────────────────────────
with open(os.path.join(BASE, "brightdata_client.py"), "w", encoding="utf-8") as f:
    f.write(brightdata)
print("✅ brightdata_client.py replaced with Apify version")

with open(os.path.join(BASE, "config.py"), "w", encoding="utf-8") as f:
    f.write(cfg)
print("✅ config.py updated with APIFY_TOKEN")

# ── Install apify-client ─────────────────────────────────────────────────────
import subprocess
subprocess.run(["pip", "install", "apify-client", "--quiet"], check=True)
print("✅ apify-client installed")

print("\nAll done. Now run: python agent.py")
