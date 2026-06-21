import os
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY       = os.getenv("ANTHROPIC_API_KEY")
APIFY_TOKEN             = os.getenv("APIFY_TOKEN")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", r"C:\Users\Dell Core i7\credentials.json")
GOOGLE_SHEET_ID         = os.getenv("GOOGLE_SHEET_ID")
ACTIVITY_WINDOW_DAYS    = int(os.getenv("ACTIVITY_WINDOW_DAYS", 10))
OUTREACH_SERVICE_PITCH  = os.getenv("OUTREACH_SERVICE_PITCH", "we help business owners automate their LinkedIn outreach")
OUTREACH_SOFT_CTA       = os.getenv("OUTREACH_SOFT_CTA", "Would you be open to a quick chat?")
COLUMNS = ["Name", "LinkedIn URL", "Email", "Headline", "Service Section", "About Section", "Recent Activity", "Status", "Commented On (Author)", "Commented Post Topic", "AI Draft Message", "Scraped At"]
MESSAGES_COLUMNS = ["Name", "LinkedIn URL", "Email", "Personalized Message", "Scraped At"]
NICHES_TAB, ACTIVE_TAB, INACTIVE_TAB, MESSAGES_TAB = "Niches", "Active", "Inactive", "Messages"
