# Fix 2: api/index.py - prevent duplicate runs + fix sheet_id passing
path = r"C:\mythos-real\api\index.py"
content = open(path, encoding="utf-8").read()

# Fix SheetsClient constructor - sheets.py doesnt accept sheet_id in __init__
old1 = '''class SheetsClient:
    def __init__(self):'''
path2 = r"C:\mythos-real\sheets.py"
content2 = open(path2, encoding="utf-8").read()
old2 = '''class SheetsClient:
    def __init__(self):
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")'''
new2 = '''class SheetsClient:
    def __init__(self, sheet_id=None):
        if sheet_id:
            import config as _config
            _config.GOOGLE_SHEET_ID = sheet_id
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")'''

if old2 in content2:
    content2 = content2.replace(old2, new2)
    open(path2, "w", encoding="utf-8").write(content2)
    print("sheets.py FIXED - sheet_id support added")
else:
    print("sheets.py - checking existing...")
    idx = content2.find("class SheetsClient")
    print(content2[idx:idx+200])
