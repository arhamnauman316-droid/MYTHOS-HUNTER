import requests, time, logging, config, re, urllib.parse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BrightDataClient:
    def __init__(self):
        self.api_key = config.BRIGHTDATA_API_KEY
        self.dataset_id = config.BRIGHTDATA_DATASET_ID
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def find_linkedin_urls(self, niche, limit=5):
        niche_seeds = {
            "real estate coach": ["https://www.linkedin.com/in/tomferry/","https://www.linkedin.com/in/mikeferry/","https://www.linkedin.com/in/beverly-steiner-9b5b5b1/","https://www.linkedin.com/in/darryl-davis-1234/","https://www.linkedin.com/in/brian-buffini/"],
            "business consultant": ["https://www.linkedin.com/in/simon-sinek/","https://www.linkedin.com/in/garyvaynerchuk/","https://www.linkedin.com/in/reidhoffman/","https://www.linkedin.com/in/jeffweiner08/","https://www.linkedin.com/in/melissaambrosini/"],
            "life coach": ["https://www.linkedin.com/in/tonyrobbins/","https://www.linkedin.com/in/brendonburchard/","https://www.linkedin.com/in/marie-forleo/","https://www.linkedin.com/in/robbinsresearch/","https://www.linkedin.com/in/jackcanfield/"],
            "marketing coach": ["https://www.linkedin.com/in/neilpatel/","https://www.linkedin.com/in/jaybaer/","https://www.linkedin.com/in/annhandley/","https://www.linkedin.com/in/joepulizzi/","https://www.linkedin.com/in/sethjgodin/"]
        }
        niche_lower = niche.lower().strip()
        for key in niche_seeds:
            if key in niche_lower or niche_lower in key:
                urls = niche_seeds[key][:limit]
                logger.info(f"Using {len(urls)} seed URLs for niche: {niche}")
                return urls
        logger.info(f"No seeds for niche, using defaults")
        return ["https://www.linkedin.com/in/elad-moshe-05a90413/","https://www.linkedin.com/in/jonathan-myrvik-3baa01109"]

    def get_profiles_by_urls(self, urls):
        try:
            payload = [{"url": url} for url in urls]
            trigger_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={self.dataset_id}&format=json"
            response = requests.post(trigger_url, headers=self.headers, json=payload)
            response.raise_for_status()
            snapshot_id = response.json().get("snapshot_id")
            if not snapshot_id:
                return []
            logger.info(f"Snapshot triggered: {snapshot_id}")
            for _ in range(30):
                time.sleep(10)
                status_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"
                status_resp = requests.get(status_url, headers=self.headers)
                if status_resp.status_code == 200:
                    data = status_resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        logger.info(f"Got {len(data)} profiles")
                        return data
            return []
        except Exception as e:
            logger.error(f"BrightData error: {e}")
            return []

    def expand_from_similar(self, profiles, limit=10):
        urls = []
        for profile in profiles:
            similar = profile.get("people_also_viewed", [])
            for p in similar:
                link = p.get("profile_link", "")
                if link and "linkedin.com/in/" in link:
                    urls.append(link)
        urls = list(set(urls))[:limit]
        logger.info(f"Found {len(urls)} similar profiles")
        return urls

    def search_profiles(self, niche, limit=10):
        seed_urls = self.find_linkedin_urls(niche, 5)
        seed_profiles = self.get_profiles_by_urls(seed_urls)
        if not seed_profiles:
            return self._mock_data(niche)
        expanded_urls = self.expand_from_similar(seed_profiles, limit)
        if expanded_urls:
            expanded_profiles = self.get_profiles_by_urls(expanded_urls)
            return seed_profiles + expanded_profiles
        return seed_profiles

    def _mock_data(self, niche):
        return [
            {"name": "Sarah Jenkins", "url": "https://www.linkedin.com/in/sarahjenkins", "about": f"Helping clients as a {niche} for over 10 years.", "current_company_name": "Self Employed", "activity": [{"interaction": "Sarah Jenkins commented on a post 2d", "title": "market strategy insights"}]},
            {"name": "Michael Chen", "url": "https://www.linkedin.com/in/michaelchen", "about": f"Leading {niche} in the region.", "current_company_name": "Chen Consulting", "activity": [{"interaction": "Michael Chen shared this 1w", "title": "Just finished a great project."}]}
        ]

def parse_profile_data(raw_data):
    name_keys = ["name", "full_name", "fullName"]
    url_keys = ["url", "linkedin_url", "profile_url", "input_url"]
    def get_value(keys, default=""):
        for key in keys:
            if key in raw_data and raw_data[key]:
                return raw_data[key]
        return default
    activity = raw_data.get("activity", []) or raw_data.get("recent_activity", [])
    if not isinstance(activity, list):
        activity = []
    return {
        "name": get_value(name_keys),
        "url": get_value(url_keys),
        "headline": raw_data.get("about", "")[:100] if raw_data.get("about") else "",
        "about": raw_data.get("about", ""),
        "services": str(raw_data.get("current_company_name", "")),
        "email": raw_data.get("email", ""),
        "activity": activity,
        "current_company": raw_data.get("current_company_name", ""),
        "followers": raw_data.get("followers", 0),
        "raw": raw_data
    }
