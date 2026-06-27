import sys
sys.path.insert(0, r"C:\mythos-real")
import config
from sheets import SheetsClient

sc = SheetsClient()
print("All tabs in this spreadsheet:")
for ws in sc.sheet.worksheets():
    print(f"  - title={ws.title!r}  gid={ws.id}  rows_with_data={len(ws.get_all_values())}")
