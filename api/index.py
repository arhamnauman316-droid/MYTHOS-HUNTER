from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import threading, sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import agent, config
from sheets import SheetsClient

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

job_status = {"running": False, "log": [], "done": False}

def run_agent():
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
        agent.run()
        job_status["log"].append("✅ Done! Check your Google Sheet for leads.")
    except Exception as e:
        job_status["log"].append(f"❌ Error: {e}")
    finally:
        job_status["running"] = False
        job_status["done"] = True

@app.post("/start")
def start():
    if job_status["running"]:
        return {"status": "already running"}
    threading.Thread(target=run_agent).start()
    return {"status": "started"}

@app.get("/status")
def status():
    return job_status

@app.get("/leads")
def get_leads():
    try:
        sc = SheetsClient()
        active_ws = sc.sheet.worksheet(config.ACTIVE_TAB)
        inactive_ws = sc.sheet.worksheet(config.INACTIVE_TAB)
        active = active_ws.get_all_records()
        inactive = inactive_ws.get_all_records()
        print(f"Active leads: {len(active)}, Inactive leads: {len(inactive)}")
        return {"active": active, "inactive": inactive}
    except Exception as e:
        print(f"Leads error: {str(e)}")
        return {"active": [], "inactive": [], "error": str(e)}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Mythos Hunter</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; min-height: 100vh; }
.header { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center; border-bottom: 1px solid #333; }
.header h1 { font-size: 2.5em; background: linear-gradient(90deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header p { color: #888; margin-top: 8px; }
.container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
.card { background: #111; border: 1px solid #222; border-radius: 12px; padding: 24px; margin-bottom: 24px; }
.btn { background: linear-gradient(135deg, #6366f1, #a855f7); color: white; border: none; padding: 14px 40px; border-radius: 8px; font-size: 1.1em; cursor: pointer; transition: opacity 0.2s; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.log { background: #0a0a0a; border: 1px solid #222; border-radius: 8px; padding: 16px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.85em; color: #0f0; }
.log p { margin: 2px 0; }
.tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab { padding: 8px 20px; border-radius: 6px; cursor: pointer; background: #222; border: none; color: #888; }
.tab.active { background: #6366f1; color: white; }
table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
th { background: #1a1a1a; padding: 10px; text-align: left; color: #6366f1; border-bottom: 1px solid #333; }
td { padding: 10px; border-bottom: 1px solid #1a1a1a; color: #ccc; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
tr:hover td { background: #151515; }
.badge { padding: 3px 10px; border-radius: 20px; font-size: 0.75em; }
.badge.active { background: #064e3b; color: #34d399; }
.badge.inactive { background: #1f2937; color: #9ca3af; }
.sheet-link { color: #6366f1; text-decoration: none; }
.sheet-link:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="header">
  <h1>🎯 Mythos Hunter</h1>
  <p>AI-powered LinkedIn lead generation</p>
</div>
<div class="container">
  <div class="card">
    <h2 style="margin-bottom:16px">Find Leads</h2>
    <p style="color:#888;margin-bottom:20px">Searches LinkedIn for leads based on niches in your Google Sheet, scrapes profiles, and drafts personalized messages with AI.</p>
    <button class="btn" id="startBtn" onclick="startHunt()">🚀 Start Hunting</button>
    <a href="https://docs.google.com/spreadsheets/d/1kccIFoo1NicWTv-QD5o4Yu1dg3XQ-KylcT6MYn3y6H0" target="_blank" class="sheet-link" style="margin-left:20px">📊 Open Google Sheet</a>
  </div>
  <div class="card">
    <h2 style="margin-bottom:16px">Live Log</h2>
    <div class="log" id="log"><p style="color:#444">Waiting to start...</p></div>
  </div>
  <div class="card">
    <h2 style="margin-bottom:16px">Leads</h2>
    <div class="tabs">
      <button class="tab" onclick="showTab('active', event)">Active</button>
      <button class="tab active" onclick="showTab('inactive', event)">Inactive</button>
    </div>
    <div id="leadsTable"></div>
  </div>
</div>
<script>
let polling = null;
let currentTab = 'inactive';
let leadsData = {active: [], inactive: []};

function startHunt() {
  document.getElementById('startBtn').disabled = true;
  document.getElementById('startBtn').textContent = '⏳ Hunting...';
  document.getElementById('log').innerHTML = '';
  fetch('/start', {method:'POST'}).then(() => {
    polling = setInterval(checkStatus, 2000);
  });
}

function checkStatus() {
  fetch('/status').then(r=>r.json()).then(data => {
    const log = document.getElementById('log');
    log.innerHTML = data.log.map(l=>`<p>${l}</p>`).join('');
    log.scrollTop = log.scrollHeight;
    if (data.done) {
      clearInterval(polling);
      document.getElementById('startBtn').disabled = false;
      document.getElementById('startBtn').textContent = '🚀 Start Hunting';
      loadLeads();
    }
  });
}

function loadLeads() {
  fetch('/leads').then(r=>r.json()).then(data => {
    leadsData = data;
    renderTable();
  });
}

function showTab(tab, e) {
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  if (e) e.target.classList.add('active');
  renderTable();
}

function renderTable() {
  const leads = leadsData[currentTab] || [];
  if (!leads.length) {
    document.getElementById('leadsTable').innerHTML = '<p style="color:#444;padding:20px">No leads yet. Click Start Hunting!</p>';
    return;
  }
  const cols = ['Name','LinkedIn URL','Headline','Recent Activity','Status','AI Draft Message'];
  let html = '<table><tr>' + cols.map(c=>`<th>${c}</th>`).join('') + '</tr>';
  leads.forEach(lead => {
    html += '<tr>';
    cols.forEach(col => {
      let val = lead[col] || '';
      if (col === 'LinkedIn URL') val = `<a href="${val}" target="_blank" style="color:#6366f1">${val}</a>`;
      if (col === 'Status') val = `<span class="badge ${val.toLowerCase()}">${val}</span>`;
      html += `<td title="${val}">${val}</td>`;
    });
    html += '</tr>';
  });
  html += '</table>';
  document.getElementById('leadsTable').innerHTML = html;
}

loadLeads();
</script>
</body>
</html>"""