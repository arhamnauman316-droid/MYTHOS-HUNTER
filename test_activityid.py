import re
from datetime import datetime, timezone

def activity_id_to_date(url):
    match = re.search(r"activity-(\d+)", url)
    if not match:
        return None
    activity_id = int(match.group(1))
    timestamp_ms = activity_id >> 22
    timestamp_s = timestamp_ms / 1000
    return datetime.fromtimestamp(timestamp_s, tz=timezone.utc)

def is_active(url):
    post_date = activity_id_to_date(url)
    if not post_date:
        return False
    days_ago = (datetime.now(timezone.utc) - post_date).days
    return days_ago <= 7

urls = [
    "https://www.linkedin.com/posts/smithhmackenzie_blood-pressure-activity-7476273312801697792-Ifn3",
    "https://www.linkedin.com/posts/smithhmackenzie_epic-morning-routine-activity-7475548709234290689-9pXj",
    "https://www.linkedin.com/posts/smithhmackenzie_you-are-100-responsible-for-your-life-and-activity-7287514704007041024-9cAJ",
]
for u in urls:
    d = activity_id_to_date(u)
    print(f"Posted: {d.strftime('%Y-%m-%d %H:%M UTC') if d else 'Unknown'} | Active: {is_active(u)}")
