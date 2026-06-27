import re
content = open(r"C:\mythos-real\agent.py", encoding="utf-8").read()
start = content.find("def process_lead")
end = content.find("def run(")
print(repr(content[start:end]))
