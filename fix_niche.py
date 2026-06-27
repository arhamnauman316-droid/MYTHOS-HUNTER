# Fix 1: agent.py - use UI niche, fix sheet_id passing
path = r"C:\mythos-real\agent.py"
content = open(path, encoding="utf-8").read()

old = '''def run(niche=None, sheet_id=None):
    logger.info("Mythos Hunter starting...")
    bd_client = BrightDataClient()
    sheets_client = SheetsClient(sheet_id=sheet_id) if sheet_id else SheetsClient()
    niches = [niche] if niche else sheets_client.get_niches()
    logger.info(f"Found niches: {niches}")'''

new = '''def run(niche=None, sheet_id=None):
    logger.info("Mythos Hunter starting...")
    bd_client = BrightDataClient()
    sheets_client = SheetsClient(sheet_id=sheet_id) if sheet_id else SheetsClient()
    # Always use UI niche if provided - never fall back to Sheet
    if niche and niche.strip():
        niches = [niche.strip()]
    else:
        niches = sheets_client.get_niches()
    logger.info(f"Hunting niche: {niches[0] if niches else 'none'}")'''

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("agent.py FIXED")
else:
    print("agent.py NOT FOUND - showing current run function:")
    idx = content.find("def run(")
    print(content[idx:idx+300])
