import requests
resp = requests.post(
    "https://api.apollo.io/api/v1/people/match",
    headers={"Content-Type": "application/json", "X-Api-Key": "O_w6vzp6Jw6vdzBa8W5k1g"},
    json={"linkedin_url": "https://www.linkedin.com/in/tomferry"},
    timeout=30,
)
print("Status:", resp.status_code)
print("Response:", resp.text[:1000])
