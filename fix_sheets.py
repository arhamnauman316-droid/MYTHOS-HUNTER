path = r"C:\mythos-real\sheets.py"
content = open(path, encoding="utf-8").read()
old = '''                row = [
                    lead.get("name", ""),
                    lead.get("url", ""),
                    lead.get("email", ""),
                    lead.get("headline", ""),
                    lead.get("services", ""),
                    lead.get("about", ""),
                    lead.get("Recent Activity", ""),
                    lead.get("Status", ""),
                    lead.get("Commented On (Author)", ""),
                    lead.get("Commented Post Topic", ""),
                    lead.get("AI Draft Message", ""),
                    lead.get("Scraped At", "")
                ]'''
new = '''                row = [
                    lead.get("name") or lead.get("Name") or "",
                    lead.get("url") or lead.get("LinkedIn URL") or "",
                    lead.get("email") or lead.get("Email") or "",
                    lead.get("headline") or lead.get("Headline") or "",
                    lead.get("services") or lead.get("Service Section") or "",
                    lead.get("about") or lead.get("About Section") or "",
                    lead.get("Recent Activity") or "",
                    lead.get("Status") or "",
                    lead.get("Commented On (Author)") or "",
                    lead.get("Commented Post Topic") or "",
                    lead.get("AI Draft Message") or "",
                    lead.get("Scraped At") or lead.get("scraped_at") or ""
                ]'''
if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("sheets.py FIXED")
else:
    print("NOT FOUND - check manually")
