import requests, time, logging, config
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class BrightDataClient:
    def __init__(self, api_key: str = config.BRIGHTDATA_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.brightdata.com"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def search_profiles(self, niche: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.api_key or self.api_key == "your_brightdata_api_key":
            return [
                {"name": "Sarah Jenkins", "url": "https://www.linkedin.com/in/sarahjenkins-mock", "headline": f"Experienced {niche}", "about": f"Helping clients succeed as a {niche} for over 10 years.", "recent_activity": [{"type": "comment", "date": "2 days ago", "post_author": "Alex Rivera", "post_topic": "market strategy"}]},
                {"name": "Michael Chen", "url": "https://www.linkedin.com/in/michaelchen-mock", "headline": f"Top {niche} in the Region", "recent_activity": [{"type": "post", "date": "20 days ago", "text": "Just finished a great project."}]}
            ]
        # Real logic for Bright Data goes here
        return []

def parse_profile_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    name_keys = ['name', 'full_name', 'fullName']
    url_keys = ['url', 'linkedin_url', 'profile_url']
    def get_value(keys, default=""):
        for key in keys:
            if key in raw_data and raw_data[key]: return raw_data[key]
        return default
    activity = raw_data.get('recent_activity', []) or raw_data.get('posts', [])
    if not isinstance(activity, list): activity = []
    return {"name": get_value(name_keys), "url": get_value(url_keys), "headline": raw_data.get('headline', ""), "about": raw_data.get('about', ""), "services": str(raw_data.get('services', "")), "email": raw_data.get('email', ""), "activity": activity, "raw": raw_data}
