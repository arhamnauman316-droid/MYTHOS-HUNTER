content = open(r"C:\mythos-real\agent.py", encoding="utf-8").read()
start = content.find("def parse_profile_data")
if start == -1:
    print("parse_profile_data not found in agent.py - checking other files")
else:
    end = content.find("\ndef ", start + 10)
    if end == -1:
        end = len(content)
    print(repr(content[start:end]))
