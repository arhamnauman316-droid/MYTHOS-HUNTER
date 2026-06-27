path = r"C:\mythos-real\agent.py"
content = open(path, encoding="utf-8").read()
content = content.replace(
    'ai_draft = draft_message(profile["name"], author, topic)',
    'ai_draft = draft_message(profile.get("name") or profile.get("fullName") or "there", author, topic)'
)
open(path, "w", encoding="utf-8").write(content)
print("DONE" if 'profile.get("name")' in open(path).read() else "FAILED")
