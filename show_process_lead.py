content = open(r"C:\mythos-real\agent.py", encoding="utf-8").read()
start = content.find("def process_lead")
if start == -1:
    print("process_lead not found, dumping whole file instead")
    print(repr(content))
else:
    end = content.find("\ndef ", start + 10)
    if end == -1:
        end = len(content)
    print(repr(content[start:end]))
