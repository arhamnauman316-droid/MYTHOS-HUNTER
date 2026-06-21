import re
from datetime import datetime, timedelta
from typing import Optional, Union

def parse_linkedin_date(date_str: Union[str, int, float, None]) -> Optional[datetime]:
    if date_str is None: return None
    if isinstance(date_str, (int, float)):
        try: return datetime.fromtimestamp(date_str)
        except: return None
    date_str = str(date_str).strip().lower()
    now = datetime.now()
    if "today" in date_str: return now
    if "yesterday" in date_str: return now - timedelta(days=1)

    # Handle formats like "2d", "3w", "1m", "5h"
    match = re.search(r'(\d+)\s*([dwmh])', date_str)
    if match:
        value, unit = int(match.group(1)), match.group(2)
        if unit == 'd': return now - timedelta(days=value)
        if unit == 'w': return now - timedelta(weeks=value)
        if unit == 'm': return now - timedelta(days=value * 30)
        if unit == 'h': return now - timedelta(hours=value)

    # Handle formats like "2 days ago", "3 weeks ago", etc.
    match = re.search(r'(\d+)\s+(day|days|week|weeks|month|months|hour|hours)\s+ago', date_str)
    if match:
        value, unit = int(match.group(1)), match.group(2)
        if unit.startswith('day'): return now - timedelta(days=value)
        if unit.startswith('week'): return now - timedelta(weeks=value)
        if unit.startswith('month'): return now - timedelta(days=value * 30)
        if unit.startswith('hour'): return now - timedelta(hours=value)

    return None

def classify_profile(last_activity_date: Optional[datetime], window_days: int = 10) -> str:
    if not last_activity_date: return "Inactive"
    days_ago = (datetime.now() - last_activity_date).days
    return "Active" if days_ago <= window_days else "Inactive"

def humanize_days_ago(date_obj: Optional[datetime]) -> str:
    if not date_obj: return "Unknown"
    days = (datetime.now() - date_obj).days
    if days == 0: return "Today"
    if days == 1: return "Yesterday"
    if days < 7: return f"{days} days ago"
    if days < 30: return f"{days // 7} weeks ago"
    return f"{days // 30} months ago"
