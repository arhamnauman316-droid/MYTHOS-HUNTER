content = open(r"C:\mythos-real\brightdata_client.py", encoding="utf-8").read()
start = content.find("def find_linkedin_urls")
end = content.find("\ndef ", start + 10)
print(repr(content[start:end]))
