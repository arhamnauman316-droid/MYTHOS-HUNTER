path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()

old = '''            try:
                q = f\'"{name}" linkedin post {company}\'.strip()
                any_results = _serp(q, num=3)
                if any_results:
                    post_text = any_results[0].get("snippet", "")[:300]
                    post_date = any_results[0].get("date", "")
                    # Active if date snippet contains recent time indicators
                    recent_words = [
                        "hour", "minute", "today", "yesterday",
                        "1 day", "2 day", "3 day", "4 day", "5 day", "6 day", "7 day",
                        "1d ago", "2d ago", "3d ago", "4d ago", "5d ago", "6d ago", "7d ago",
                    ]
                    combined = (post_text + " " + post_date).lower()
                    is_active = any(w in combined for w in recent_words)
                    if not post_date:
                        post_date = "Within 7 days" if is_active else "Over a week ago"
            except Exception as e:
                logger.warning(f"Post search failed for {name}: {e}")'''

new = '''            try:
                slug = url.split("linkedin.com/in/")[1].rstrip("/")
                # Search 1: recent posts from this specific profile (last 7 days)
                q_recent = f"site:linkedin.com {slug} OR {name}"
                recent_results = _serp(q_recent + " tbs:qdr:w", num=3)
                # Search 2: any post to get content
                q_post = f\'"{name}" site:linkedin.com post\'
                post_results = _serp(q_post, num=3)

                # Get post content from any result
                for pr in post_results:
                    psnippet = pr.get("snippet", "")
                    pdate = pr.get("date", "")
                    plink = pr.get("link", "")
                    if "linkedin.com" in plink and psnippet:
                        post_text = psnippet[:300]
                        post_date = pdate
                        # Check if active based on date
                        recent_words = [
                            "hour", "hours", "minute", "minutes",
                            "today", "yesterday",
                            "1 day", "2 day", "3 day", "4 day", "5 day", "6 day", "7 day",
                            "ago"
                        ]
                        combined = (post_text + " " + post_date).lower()
                        # Active if posted recently (date field has "X hours/days ago")
                        if pdate and any(w in pdate.lower() for w in ["hour", "minute", "day ago", "days ago", "yesterday", "today"]):
                            # Check if within 7 days
                            import re as _re
                            day_match = _re.search(r"(\d+)\s*day", pdate.lower())
                            if day_match:
                                days = int(day_match.group(1))
                                is_active = days <= 7
                            else:
                                is_active = True  # hours/minutes = definitely active
                        break

                if not post_date:
                    post_date = "Within 7 days" if is_active else "Over a week ago"
            except Exception as e:
                logger.warning(f"Post search failed for {name}: {e}")'''

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("FIXED")
else:
    print("NOT FOUND")
