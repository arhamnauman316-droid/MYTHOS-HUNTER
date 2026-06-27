import os
files = ["agent.py", "brightdata_client.py", "sheets.py", "activity.py", "drafter.py", "config.py", "main.py"]
base = r"C:\mythos-real"
for fname in files:
    path = os.path.join(base, fname)
    if not os.path.exists(path):
        continue
    content = open(path, encoding="utf-8").read()
    if "def parse_profile_data" in content:
        print(f"FOUND in {fname}")
        start = content.find("def parse_profile_data")
        end = content.find("\ndef ", start + 10)
        if end == -1:
            end = len(content)
        print(repr(content[start:end]))

# also print the top imports of agent.py to see where it's imported from
print("\n--- agent.py imports ---")
agent_content = open(os.path.join(base, "agent.py"), encoding="utf-8").read()
print(agent_content[:500])
