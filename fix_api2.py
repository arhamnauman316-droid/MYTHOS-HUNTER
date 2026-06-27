# Fix 3: api/index.py - prevent duplicate runs with lock
path = r"C:\mythos-real\api\index.py"
content = open(path, encoding="utf-8").read()

old = '''@app.post("/start")
def start(req: StartRequest = None):
    if job_status["running"]:
        return {"status": "already running"}
    niche = (req.niche or "").strip() or None
    sheet_id = (req.sheet_id or "").strip() or None
    threading.Thread(target=run_agent, kwargs={"niche": niche, "sheet_id": sheet_id}).start()
    return {"status": "started"}'''

new = '''@app.post("/start")
def start(req: StartRequest = None):
    if job_status["running"]:
        return {"status": "already running"}
    niche = (req.niche or "").strip() or None
    sheet_id = (req.sheet_id or "").strip() or None
    if not niche:
        return {"status": "error", "message": "Please enter a niche"}
    job_status["running"] = True  # Set immediately to prevent duplicates
    t = threading.Thread(target=run_agent, kwargs={"niche": niche, "sheet_id": sheet_id})
    t.daemon = True
    t.start()
    return {"status": "started", "niche": niche}'''

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("api/index.py FIXED - duplicate prevention added")
else:
    print("NOT FOUND")
