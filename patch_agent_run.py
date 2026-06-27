path = r"C:\mythos-real\agent.py"
content = open(path, encoding="utf-8").read()

old = 'def run():\n    logger.info("Mythos Hunter starting...")\n    bd_client = BrightDataClient()\n    sheets_client = SheetsClient()\n    niches = sheets_client.get_niches()'

new = 'def run(niche=None, sheet_id=None):\n    logger.info("Mythos Hunter starting...")\n    bd_client = BrightDataClient()\n    sheets_client = SheetsClient(sheet_id=sheet_id) if sheet_id else SheetsClient()\n    niches = [niche] if niche else sheets_client.get_niches()'

if old not in content:
    print("ERROR: not found")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
