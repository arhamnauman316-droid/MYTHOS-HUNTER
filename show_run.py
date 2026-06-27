content = open(r"C:\mythos-real\agent.py", encoding="utf-8").read()
start = content.find("def run(")
end = content.find("\ndef ", start + 5)
print(repr(content[start:end]))
