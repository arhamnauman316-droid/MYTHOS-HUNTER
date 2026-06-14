import gspread, json, config, logging
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SheetsClient:
    def __init__(self, credentials_json: str = config.GOOGLE_SHEETS_CREDENTIALS_JSON, sheet_id: str = config.GOOGLE_SHEET_ID):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        try:
            if config.GOOGLE_SHEETS_CREDENTIALS_CONTENT:
                creds_dict = json.loads(config.GOOGLE_SHEETS_CREDENTIALS_CONTENT)
                self.creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            else: self.creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, self.scope)
            self.client = gspread.authorize(self.creds)
        except Exception as e: logger.error(f"Auth Error: {e}"); self.spreadsheet = None; return

        if not sheet_id or sheet_id in ["your_google_sheet_id", "None"]:
            logger.info("Creating a brand new Mythos Lead Sheet...")
            try: self.spreadsheet = self.client.create("Mythos Autonomous Leads")
            except: self.spreadsheet = None
        else:
            try: self.spreadsheet = self.client.open_by_key(sheet_id)
            except: self.spreadsheet = None

    def _get_or_create_tab(self, tab_name: str, headers: List[str] = None):
        if not self.spreadsheet: return None
        try: return self.spreadsheet.worksheet(tab_name)
        except:
            ws = self.spreadsheet.add_worksheet(title=tab_name, rows="100", cols="20")
            if headers: ws.append_row(headers)
            return ws

    def get_niches(self) -> List[str]:
        if not self.spreadsheet: return ["Real Estate Coach"]
        ws = self._get_or_create_tab(config.NICHES_TAB, ["Niche Search Keyword"])
        niches = ws.col_values(1)[1:]
        if not niches: ws.append_row(["Real Estate Coach"]); return ["Real Estate Coach"]
        return [n.strip() for n in niches if n.strip()]

    def save_leads(self, leads: List[Dict[str, Any]]):
        if not self.spreadsheet: return
        for lead in leads:
            tab_name = config.ACTIVE_TAB if lead.get("Status") == "ACTIVE" else config.INACTIVE_TAB
            ws = self._get_or_create_tab(tab_name, config.COLUMNS)
            ws.append_row([lead.get(col, "") for col in config.COLUMNS])
