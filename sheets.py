import gspread, config, logging
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

class SheetsClient:
    def __init__(self):
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
            # Create using Sheets API directly (no Drive storage needed)
            sh = self.client.create("Mythos Hunter Leads")
            # Share with anyone so client can access
            sh.share(None, perm_type='anyone', role='writer')
            logger.info(f"Sheet created: {sh.url}")
            print(f"\n✅ Sheet created! Share this URL with your client:\n{sh.url}\n")
            self._ensure_tabs(sh)
            # Save sheet ID to env for next run
            with open(".env", "a") as f:
                f.write(f"\nGOOGLE_SHEET_ID={sh.id}")
            return sh
        except Exception as e:
            logger.error(f"Sheet error: {e}")
            raise

    def _ensure_tabs(self, sh):
        existing = [ws.title for ws in sh.worksheets()]
        for tab in [config.NICHES_TAB, config.ACTIVE_TAB, config.INACTIVE_TAB]:
            if tab not in existing:
                sh.add_worksheet(title=tab, rows=1000, cols=20)
        if config.NICHES_TAB in [ws.title for ws in sh.worksheets()]:
            niches_ws = sh.worksheet(config.NICHES_TAB)
            if niches_ws.row_count == 0 or not niches_ws.get_all_values():
                niches_ws.append_row(["Niche"])
                niches_ws.append_row(["real estate coach"])
                niches_ws.append_row(["business consultant"])
        if config.ACTIVE_TAB in [ws.title for ws in sh.worksheets()]:
            active_ws = sh.worksheet(config.ACTIVE_TAB)
            if not active_ws.get_all_values():
                active_ws.append_row(config.COLUMNS)
        if config.INACTIVE_TAB in [ws.title for ws in sh.worksheets()]:
            inactive_ws = sh.worksheet(config.INACTIVE_TAB)
            if not inactive_ws.get_all_values():
                inactive_ws.append_row(config.COLUMNS)
        # Remove default Sheet1 if exists
        try:
            sh.del_worksheet(sh.worksheet("Sheet1"))
        except:
            pass

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
                    lead.get("AI Draft Message", "")
                ]
                ws.append_row(row)
            logger.info(f"Saved {len(leads)} leads to {tab}")
        except Exception as e:
            logger.error(f"Error saving leads: {e}")