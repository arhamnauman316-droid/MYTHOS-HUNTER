path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
content = content.replace("from ddgs import DDCS", "from ddgs import DDGS")
content = content.replace("with DDCS()", "with DDGS()")
open(path, "w", encoding="utf-8").write(content)
print("DONE")
