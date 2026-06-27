path = r"C:\mythos-real\brightdata_client.py"
content = open(path, encoding="utf-8").read()

old = '''            try:
                q = f"{name} {company} linkedin post".strip()
                gr = requests.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={"key": GOOGLE_KEY, "cx": GOOGLE_CX, "num": 1, "q": q},
                    timeout=15,
                )
                items = gr.json().get("items") or []
                if items:
                    item = items[0]
                    post_text = item.get("snippet", "")[:200]
                    pagemap = item.get("pagemap") or {}
                    metatags = (pagemap.get("metatags") or [{}])[0]
                    pub_time = (
                        metatags.get("article:published_time") or
                        metatags.get("og:updated_time") or ""
                    )
                    if pub_time:
                        post_date = pub_time[:10]
                        try:
                            days_ago = (date.today() - date.fromisoformat(post_date)).days
                            is_active = days_ago <= 30
                        except Exception:
                            is_active = True
                    else:
                        is_active = bool(post_text)
                        post_date = "Recently"
            except Exception as e:
                logger.warning(f"Google search failed for {name}: {e}")'''

new = '''            try:
                from ddgs import DDGS
                q = f"{name} {company} linkedin post".strip()
                with DDGS() as ddgs:
                    presults = list(ddgs.text(q, max_results=3))
                for pr in presults:
                    plink = pr.get("href", "")
                    if "linkedin.com" in plink:
                        post_text = pr.get("body", "")[:200]
                        post_date = "Recently"
                        is_active = True
                        break
                else:
                    if presults:
                        post_text = presults[0].get("body", "")[:200]
                        post_date = "Recently"
                        is_active = True
            except Exception as e:
                logger.warning(f"DDG post search failed for {name}: {e}")'''

if old in content:
    content = content.replace(old, new)
    open(path, "w", encoding="utf-8").write(content)
    print("DONE")
else:
    print("ERROR: not found")
