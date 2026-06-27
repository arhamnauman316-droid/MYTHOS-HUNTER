import re

# Remove from agent.py process_lead return
path = r"C:\mythos-real\agent.py"
content = open(path, encoding="utf-8").read()
old = '            "Recent Activity": humanize_days_ago(last_date),\n'
if old in content:
    content = content.replace(old, "")
    open(path, "w", encoding="utf-8").write(content)
    print("Removed from agent.py")
else:
    print("Not found in agent.py")

# Remove from sheets.py column list if present
path2 = r"C:\mythos-real\sheets.py"
content2 = open(path2, encoding="utf-8").read()
if "Recent Activity" in content2:
    content2 = content2.replace('"Recent Activity", ', "").replace('"Recent Activity",\n', "").replace('"Recent Activity"', "")
    open(path2, "w", encoding="utf-8").write(content2)
    print("Removed from sheets.py")
else:
    print("Not in sheets.py")
