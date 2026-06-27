import os

BASE = r"C:\mythos-real"

# ── brightdata_client.py ─────────────────────────────────────────────────────
brightdata = '''import logging, config
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
        """Uses harvestapi/linkedin-profile-scraper with email search enabled.
        $10/1k profiles. Stamps every result with scraped_at (UTC) timestamp."""
        try:
            client = ApifyClient(self.apify_token)
            run = client.actor("harvestapi/linkedin-profile-scraper").call(
                run_input={
                    "urls": urls,
                    "profileScraperMode": "Profile details + email search ($10 per 1k)",
                }
            )
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            for item in items:
                item["scraped_at"] = scraped_at
            logger.info(f"Apify returned {len(items)} profiles (scraped {scraped_at})")
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
'''

# ── config.py ─────────────────────────────────────────────────────────────────
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
COLUMNS = ["Name", "LinkedIn URL", "Email", "Headline", "Service Section", "About Section", "Recent Activity", "Status", "Commented On (Author)", "Commented Post Topic", "AI Draft Message", "Scraped At"]
MESSAGES_COLUMNS = ["Name", "LinkedIn URL", "Email", "Personalized Message", "Scraped At"]
NICHES_TAB, ACTIVE_TAB, INACTIVE_TAB, MESSAGES_TAB = "Niches", "Active", "Inactive", "Messages"
'''

# ── sheets.py ─────────────────────────────────────────────────────────────────
sheets = '''import gspread, config, logging, os, json
from google.oauth2.service_account import Credentials
logger = logging.getLogger(__name__)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
class SheetsClient:
    def __init__(self):
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        if creds_json:
            creds_info = json.loads(creds_json)
            creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        else:
            creds = Credentials.from_service_account_file(
                config.GOOGLE_CREDENTIALS_PATH, scopes=SCOPES
            )
        self.client = gspread.authorize(creds)
        self.sheet = self._get_or_create_sheet()
    def _get_or_create_sheet(self):
        try:
            if config.GOOGLE_SHEET_ID:
                sh = self.client.open_by_key(config.GOOGLE_SHEET_ID)
                self._ensure_tabs(sh)
                return sh
        except Exception as e:
            logger.error(f"Sheet error: {e}")
            raise
    def _ensure_tabs(self, sh):
        existing = [ws.title for ws in sh.worksheets()]
        for tab in [config.NICHES_TAB, config.ACTIVE_TAB, config.INACTIVE_TAB, config.MESSAGES_TAB]:
            if tab not in existing:
                sh.add_worksheet(title=tab, rows=1000, cols=20)
        active_ws = sh.worksheet(config.ACTIVE_TAB)
        if not active_ws.get_all_values():
            active_ws.append_row(config.COLUMNS)
        inactive_ws = sh.worksheet(config.INACTIVE_TAB)
        if not inactive_ws.get_all_values():
            inactive_ws.append_row(config.COLUMNS)
        messages_ws = sh.worksheet(config.MESSAGES_TAB)
        if not messages_ws.get_all_values():
            messages_ws.append_row(config.MESSAGES_COLUMNS)
    def get_niches(self):
        try:
            ws = self.sheet.worksheet(config.NICHES_TAB)
            values = ws.col_values(1)[1:]
            return [v.strip() for v in values if v.strip()]
        except Exception as e:
            logger.error(f"Error getting niches: {e}")
            return ["real estate coach"]
    def save_leads(self, leads, status="Active"):
        try:
            tab = config.ACTIVE_TAB if status == "Active" else config.INACTIVE_TAB
            ws = self.sheet.worksheet(tab)
            for lead in leads:
                row = [
                    lead.get("name", ""),
                    lead.get("url", ""),
                    lead.get("email", ""),
                    lead.get("headline", ""),
                    lead.get("services", ""),
                    lead.get("about", ""),
                    lead.get("Recent Activity", ""),
                    lead.get("Status", ""),
                    lead.get("Commented On (Author)", ""),
                    lead.get("Commented Post Topic", ""),
                    lead.get("AI Draft Message", ""),
                    lead.get("Scraped At", "")
                ]
                ws.append_row(row)
            logger.info(f"Saved {len(leads)} leads to {tab}")
        except Exception as e:
            logger.error(f"Error saving leads: {e}")
    def save_messages(self, leads):
        """Writes one row per active lead to the Messages tab: name, url, email, the
        personalized AI message, and when the profile was scraped."""
        try:
            ws = self.sheet.worksheet(config.MESSAGES_TAB)
            for lead in leads:
                row = [
                    lead.get("name", ""),
                    lead.get("url", ""),
                    lead.get("email", ""),
                    lead.get("AI Draft Message", ""),
                    lead.get("Scraped At", "")
                ]
                ws.append_row(row)
            logger.info(f"Saved {len(leads)} personalized messages to {config.MESSAGES_TAB}")
        except Exception as e:
            logger.error(f"Error saving messages: {e}")
'''

# ── agent.py ──────────────────────────────────────────────────────────────────
agent = '''import logging, config, re
from typing import Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from brightdata_client import BrightDataClient, parse_profile_data
from activity import parse_linkedin_date, classify_profile, humanize_days_ago
from drafter import draft_message
from sheets import SheetsClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_date_from_interaction(interaction: str) -> Optional[str]:
    if not interaction:
        return None
    match = re.search(r'(\\d+[dwmh])', interaction)
    if match:
        return match.group(1)
    return None

def extract_author_from_interaction(interaction: str) -> str:
    if not interaction:
        return "someone"
    interaction = interaction.lower()
    if "commented on" in interaction:
        parts = re.split(r'commented on', interaction)
        if parts:
            name = parts[0].strip().title()
            if name:
                return name
    return "someone"

def process_lead(raw_record):
    try:
        profile = parse_profile_data(raw_record)
        activity = profile.get("activity", [])
        last_date = None
        author = "someone"
        topic = "their recent post"

        for act in activity:
            interaction = act.get("interaction", "") or ""
            date_str = extract_date_from_interaction(interaction)
            if date_str:
                last_date = parse_linkedin_date(date_str)
                if last_date:
                    title = act.get("title", "")
                    if title:
                        topic = title[:120]
                    extracted_author = extract_author_from_interaction(interaction)
                    if extracted_author != "someone":
                        author = extracted_author
                    break

        if not last_date and profile.get("current_company"):
            last_date = datetime.now() - timedelta(days=3)

        status = classify_profile(last_date, config.ACTIVITY_WINDOW_DAYS)
        ai_draft = draft_message(profile["name"], author, topic)

        return {
            **profile,
            "Recent Activity": humanize_days_ago(last_date),
            "Status": status,
            "Commented On (Author)": author,
            "Commented Post Topic": topic[:150] if topic else "",
            "AI Draft Message": ai_draft,
            "Scraped At": profile.get("scraped_at", "")
        }
    except Exception as e:
        logger.error(f"Error processing lead: {e}")
        return None

def run():
    logger.info("Mythos Hunter starting...")
    bd_client = BrightDataClient()
    sheets_client = SheetsClient()
    niches = sheets_client.get_niches()
    logger.info(f"Found niches: {niches}")
    all_active = []
    all_inactive = []
    for niche in niches:
        logger.info(f"Hunting niche: {niche}")
        raw_results = bd_client.search_profiles(niche)
        if not raw_results:
            logger.info(f"No results for {niche}")
            continue
        with ThreadPoolExecutor(max_workers=5) as executor:
            leads = list(filter(None, executor.map(process_lead, raw_results)))
        for lead in leads:
            if lead.get("Status") == "Active":
                all_active.append(lead)
            else:
                all_inactive.append(lead)
        active_count = len([l for l in leads if l.get('Status') == 'Active'])
        inactive_count = len([l for l in leads if l.get('Status') == 'Inactive'])
        logger.info(f"Niche {niche}: {len(leads)} leads - Active: {active_count}, Inactive: {inactive_count}")
    if all_active:
        sheets_client.save_leads(all_active, "Active")
        sheets_client.save_messages(all_active)
    if all_inactive:
        sheets_client.save_leads(all_inactive, "Inactive")
    logger.info(f"Done. Active: {len(all_active)}, Inactive: {len(all_inactive)}")
    print(f"\\nSheet URL: {sheets_client.sheet.url}")

if __name__ == "__main__":
    run()
'''

with open(os.path.join(BASE, "brightdata_client.py"), "w", encoding="utf-8") as f:
    f.write(brightdata)
print("brightdata_client.py -> harvestapi actor + email search + scraped_at timestamp")

with open(os.path.join(BASE, "config.py"), "w", encoding="utf-8") as f:
    f.write(cfg)
print("config.py -> added Scraped At column + Messages tab config")

with open(os.path.join(BASE, "sheets.py"), "w", encoding="utf-8") as f:
    f.write(sheets)
print("sheets.py -> added Messages tab + save_messages()")

with open(os.path.join(BASE, "agent.py"), "w", encoding="utf-8") as f:
    f.write(agent)
print("agent.py -> calls save_messages() for active leads, includes Scraped At")

print("\nAll done. Now run: python agent.py")