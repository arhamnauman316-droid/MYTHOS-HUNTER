path = r"C:\mythos-real\drafter.py"
content = open(path, encoding="utf-8").read()
content = content.replace("claude-haiku-4-5", "claude-haiku-4-5-20251001")
open(path, "w", encoding="utf-8").write(content)
print("DONE")
