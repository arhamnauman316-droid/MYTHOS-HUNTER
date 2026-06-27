path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()

func = '''

def parse_profile_data(raw_record):
    """Convert new profile format to what agent.py expects."""
    from datetime import date as _date
    name   = raw_record.get("fullName") or raw_record.get("name") or ""
    posts  = raw_record.get("posts", [])
    status = raw_record.get("status", "Inactive")

    activity = []
    for post in posts:
        pub  = post.get("publishedAt", "")
        text = post.get("text", "")
        interaction = ""
        if pub and pub not in ("Recently", ""):
            try:
                days_ago = (_date.today() - _date.fromisoformat(pub)).days
                if days_ago < 7:   interaction = f"{days_ago}d"
                elif days_ago < 30: interaction = f"{days_ago // 7}w"
                else:               interaction = f"{days_ago // 30}m"
            except Exception:
                interaction = "1d" if status == "Active" else "60d"
        elif pub == "Recently":
            interaction = "1d" if status == "Active" else ""
        activity.append({"interaction": interaction, "title": text[:120]})

    if status == "Active" and not any(a.get("interaction") for a in activity):
        activity = [{"interaction": "1d", "title": posts[0].get("text", "")[:120] if posts else ""}]

    return {
        "name":             name,
        "Name":             name,
        "LinkedIn URL":     raw_record.get("linkedinUrl") or raw_record.get("url") or "",
        "Email":            raw_record.get("email") or "",
        "Headline":         raw_record.get("headline") or "",
        "Service Section":  "",
        "About Section":    raw_record.get("about") or "",
        "Recent Activity":  posts[0].get("text", "") if posts else "",
        "activity":         activity,
        "scraped_at":       raw_record.get("scraped_at") or "",
    }
'''

if "def parse_profile_data" not in content:
    content += func
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
else:
    print("Already exists")
