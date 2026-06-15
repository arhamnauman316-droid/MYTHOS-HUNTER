import requests, time, logging, config, re, urllib.parse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BrightDataClient:
    def __init__(self):
        self.api_key = config.BRIGHTDATA_API_KEY
        self.dataset_id = config.BRIGHTDATA_DATASET_ID
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def find_linkedin_urls(self, niche: str, limit: int = 5) -> List[str]:
        niche_seeds = {
            "real estate coach": [
                "https://www.linkedin.com/in/tomferry/",
                "https://www.linkedin.com/in/mikeferry/",
                "https://www.linkedin.com/in/beverly-steiner-9b5b5b1/",
                "https://www.linkedin.com/in/darryl-davis-1234/",
                "https://www.linkedin.com/in/brian-buffini/"
            ],
            "business consultant": [
                "https://www.linkedin.com/in/simon-sinek/",
                "https://www.linkedin.com/in/garyvaynerchuk/",
                "https://www.linkedin.com/in/reidhoffman/",
                "https://www.linkedin.com/in/jeffweiner08/",
                "https://www.linkedin.com/in/melissaambrosini/"
            ],
            "life coach": [
                "https://www.linkedin.com/in/tonyrobbins/",
                "https://www.linkedin.com/in/brendonburchard/",
                "https://www.linkedin.com/in/marie-forleo/",
                "https://www.linkedin.com/in/robbinsresearch/",
                "https://www.linkedin.com/in/jackcanfield/"
            ],
            "marketing coach": [
                "https://www.linkedin.com/in/neilpatel/",
                "https://www.linkedin.com/in/jaybaer/",
                "https://www.linkedin.com/in/annhandley/",
                "https://www.linkedin.com/in/joepulizzi/",
                "https://www.linkedin.com/in/sethjgodin/"
            ]
        }
        niche_lower = niche.lower().strip()
        for key in niche_seeds:
            if key in niche_lower or niche_lower in key:
                urls = niche_seeds[key][:limit]
                logger.info(f"Using {len(urls)} seed URLs for niche: {niche}")
                return urls
        logger.info(f"No seeds for niche '{niche}', using default seeds")
        return [
            "https://www.linkedin.com/in/elad-moshe-05a90413/",
            "https://www.linkedin.com/in/jonathan-myrvik-3baa01109"
        ]

    def get_profiles_by_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        try:
            payload = [{"url": url} for url in urls]
            trigger_url = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={self.dataset_id}&format=json"
            response = requests.post(trigger_url, headers=self.headers, json=payload)
            response.raise_for_status()
            snapshot_id = response.json().get("snapshot_id")
            if not snapshot_id:
                logger.error("No snapshot_id returned")
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
            logger.error("Snapshot timed out")
            return []
        except Exception as e:
            logger.error(f"BrightData error: {e}")
            return []

    def expand_from_similar(self, profiles: List[Dict[str, Any]], limit: int = 10)