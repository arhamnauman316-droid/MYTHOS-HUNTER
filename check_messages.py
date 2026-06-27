import sys
sys.path.insert(0, r"C:\mythos-real")
import config
from sheets import SheetsClient

sc = SheetsClient()
ws = sc.sheet.worksheet(config.MESSAGES_TAB)
print("Sheet title:", sc.sheet.title)
print("Sheet URL:", sc.sheet.url)
print("Messages tab row count:", ws.row_count, "Current data:")
for row in ws.get_all_values():
    print(row)
