path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()

old = '''GOOGLE_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCkge8PWzrA47oiEuQ7j7WazjxmXrcdAkU")
GOOGLE_CX = os.getenv("GOOGLE_CX", "a5e1f7d62c4b04efb")'''

new = '''SERP_KEY = os.getenv("SERP_API_KEY", "773e0e5fd5d8fed34e1e699a2d95f3986277a1d264d9c17ab5c017b70cf459d0")'''

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
else:
    print("NOT FOUND - showing current top of file:")
    print(content[:500])
