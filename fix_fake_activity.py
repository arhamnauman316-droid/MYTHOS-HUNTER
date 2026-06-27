# Removes the fake "3 days ago" fallback. classify_profile(None,...) already
# correctly returns "Inactive" and humanize_days_ago(None) already correctly
# returns "Unknown" -- this fallback was overriding that with a made-up date.
path = r"C:\mythos-real\agent.py"
content = open(path, "r", encoding="utf-8").read()

old = """        if not last_date and profile.get("current_company"):
            last_date = datetime.now() - timedelta(days=3)

        status = classify_profile(last_date, config.ACTIVITY_WINDOW_DAYS)"""

new = """        status = classify_profile(last_date, config.ACTIVITY_WINDOW_DAYS)"""

if old not in content:
    print("ERROR: couldn't find the text to replace.")
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("Fixed: removed fake activity fallback. Status/Recent Activity now honest.")
