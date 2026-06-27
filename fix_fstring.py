path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
content = content.replace(
    "q = f'\"name}\" linkedin post {company}'.strip()",
    "q = f'\"{name}\" linkedin post {company}'.strip()"
)
open(path, "w", encoding="utf-8").write(content)
print("DONE")
