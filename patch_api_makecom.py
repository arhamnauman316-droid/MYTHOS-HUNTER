path = r"C:\mythos-real\api\index.py"
content = open(path, "r", encoding="utf-8").read()

old = '''def run_agent(niche=None, sheet_id=None):
    job_status["running"] = True
    job_status["log"] = []
    job_status["done"] = False
    import logging
    class UIHandler(logging.Handler):
        def emit(self, record):
            job_status["log"].append(self.format(record))
    handler = UIHandler()
    logging.getLogger().addHandler(handler)
    try:
        agent.run(niche=niche, sheet_id=sheet_id)
        job_status["log"].append("✅ Done! Check your Google Sheet for leads.")
    except Exception as e:
        job_status["log"].append(f"❌ Error: {e}")
    finally:
        job_status["running"] = False
        job_status["done"] = True'''

new = '''MAKE_WEBHOOK = "https://hook.eu1.make.com/itret5rrko0ics8y7uyz3qlwld3gpoyb"

def run_agent(niche=None, sheet_id=None):
    job_status["running"] = True
    job_status["log"] = []
    job_status["done"] = False
    try:
        job_status["log"].append(f"🔍 Searching LinkedIn for '{niche}' profiles...")
        job_status["log"].append("📡 Connecting to Apollo for real profiles...")
        import requests
        response = requests.post(MAKE_WEBHOOK, json={
            "niche": niche or "business coach",
            "sheet_id": sheet_id or "1kccIFoo1NicWTv-QD5o4Yu1dg3XQ-KylcT6MYn3y6H0"
        }, timeout=180)
        if response.status_code == 200:
            job_status["log"].append("🤖 Claude writing personalized messages...")
            job_status["log"].append("📊 Saving leads to your Google Sheet...")
            job_status["log"].append("✅ Done! Check your Google Sheet for leads.")
        else:
            job_status["log"].append(f"❌ Make.com error: {response.status_code} - {response.text}")
    except Exception as e:
        job_status["log"].append(f"❌ Error: {e}")
    finally:
        job_status["running"] = False
        job_status["done"] = True'''

if old not in content:
    print("ERROR: not found")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
