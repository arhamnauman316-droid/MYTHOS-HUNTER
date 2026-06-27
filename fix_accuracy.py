path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()

old = '''            try:
                # Use slug for exact match, fall back to name
                q = f\'linkedin.com/posts/{slug}\'
                post_results = _serp(q, num=5)
                # If no results with slug, try name
                if not post_results:
                    q = f\'"{name}" site:linkedin.com activity\'
                    post_results = _serp(q, num=5)
                now = datetime.now(timezone.utc)
                for pr in post_results:
                    plink = pr.get("link", "")
                    psnippet = pr.get("snippet", "")
                    post_datetime = _activity_id_to_date(plink)
                    if post_datetime:
                        days_ago = (now - post_datetime).days
                        post_text = psnippet[:300]
                        post_date = post_datetime.strftime("%Y-%m-%d %H:%M UTC")
                        is_active = days_ago <= 25
                        logger.info(f"{name}: last post {days_ago}d ago -> {\'Active\' if is_active else \'Inactive\'}")
                        break'''

new = '''            try:
                now = datetime.now(timezone.utc)
                # Collect all posts from multiple queries
                all_post_results = []
                for q in [
                    f\'linkedin.com/posts/{slug}\',
                    f\'"{name}" site:linkedin.com activity\',
                ]:
                    all_post_results += _serp(q, num=10)

                # Find most recent post by decoding activity ID
                best_days = None
                for pr in all_post_results:
                    plink = pr.get("link", "")
                    psnippet = pr.get("snippet", "")
                    post_datetime = _activity_id_to_date(plink)
                    if post_datetime:
                        days_ago = (now - post_datetime).days
                        if best_days is None or days_ago < best_days:
                            best_days = days_ago
                            post_text = psnippet[:300]
                            post_date = post_datetime.strftime("%Y-%m-%d %H:%M UTC")
                            is_active = days_ago <= 25
                if best_days is not None:
                    logger.info(f"{name}: last post {best_days}d ago -> {\'Active\' if is_active else \'Inactive\'}")'''

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("FIXED")
else:
    print("NOT FOUND")
