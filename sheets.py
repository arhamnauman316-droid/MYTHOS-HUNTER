import gspread, config, logging, os, json
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
