import os
from dotenv import load_dotenv

load_dotenv()

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "14ad1bc7-0290-4b51-9d03-3e755c1d2d33")
BRIGHTDATA_SCRAPER_ID = os.getenv("BRIGHTDATA_SCRAPER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEETS_CREDENTIALS_CONTENT = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON_CONTENT")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
ACTIVITY_WINDOW_DAYS = int(os.getenv("ACTIVITY_WINDOW_DAYS", 10))
OUTREACH_SERVICE_PITCH = os.getenv("OUTREACH_SERVICE_PITCH", "we help real estate coaches automate their backend operations")
OUTREACH_SOFT_CTA = os.getenv("OUTREACH_SOFT_CTA", "Would you be open to a quick chat?")
COLUMNS = ["Name", "LinkedIn URL", "Email", "Headline", "Service Section", "About Section", "Recent Activity", "Status", "Commented On (Author)", "Commented Post Topic", "AI Draft Message"]
NICHES_TAB, ACTIVE_TAB, INACTIVE_TAB = "Niches", "Active", "Inactive"
