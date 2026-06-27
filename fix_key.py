path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()
content = content.replace(
    "AIzaSyDlOLHmtBpsHOHm-QAaKxW8l4fA5QtzULo",
    "AIzaSyCkge8PWzrA47oiEuQ7j7WazjxmXrcdAkU"
)
open(path, "w", encoding="utf-8").write(content)
print("DONE")
