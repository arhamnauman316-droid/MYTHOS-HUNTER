path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

old = 'KNOWN_GOOD_RUN_ID = "wa9pUDsxe9HcNk81a"'
new = 'KNOWN_GOOD_RUN_ID = "T3MpxFi5Umq9LGqNe"'

if old not in content:
    print("ERROR: old run ID string not found. Current get_profiles_by_urls text:")
    start = content.find("def get_profiles_by_urls")
    end = content.find("def search_profiles")
    print(repr(content[start:end]))
else:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE: now reading from the corrected dataset (4 accurate real estate coaches).")
