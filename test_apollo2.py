import requests
resp = requests.post(
    "https://api.apollo.io/api/v1/mixed_people/search",
    headers={"Content-Type": "application/json", "X-Api-Key": "O_w6vzp6Jw6vdzBa8W5k1g"},
    json={"person_titles": ["fitness coach"], "per_page": 3, "page": 1},
    timeout=30,
)
print("Status:", resp.status_code)
print("Response:", resp.text[:1000])
