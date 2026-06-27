content = open(r"C:\mythos-real\brightdata_client.py", encoding="utf-8").read()
start = content.find("def get_profiles_by_urls")
end = content.find("def search_profiles")
print(repr(content[start:end]))
