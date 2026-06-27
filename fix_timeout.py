path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
content = content.replace("timeout=20,", "timeout=45,")
open(path, "w", encoding="utf-8").write(content)
print("DONE")
