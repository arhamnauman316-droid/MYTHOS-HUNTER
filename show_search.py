content = open(r"C:\mythos-real\brightdata_client.py", encoding="utf-8").read()
start = content.find("def search_profiles")
end = content.find("\nclass ", start + 10)
if end == -1:
    end = len(content)
print(repr(content[start:end]))
