import re
path = r"C:\mythos-real\api\index.py"
content = open(path, encoding="utf-8").read()
content = content.replace(
    "https://hook.eu1.make.com/itret5rrko0ics8y7uyz3qlwld3gpoyb",
    "https://hook.eu1.make.com/vekvfbsi765m26pgiyharxiw2tqotmjd"
)
open(path, "w", encoding="utf-8").write(content)
print("DONE")
