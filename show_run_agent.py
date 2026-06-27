content = open(r"C:\mythos-real\api\index.py", encoding="utf-8").read()
start = content.find("def run_agent")
end = content.find("\n@app", start)
print(repr(content[start:end]))
