path = r"C:\mythos-real\brightdata_client.py"
content = open(path, "r", encoding="utf-8").read()

# Fix all three client.run().get() calls
old1 = '            posts_run_info = client.run(POSTS_RUN_ID).get()\n            posts_items = list(client.dataset(posts_run_info["defaultDatasetId"]).iterate_items())'
new1 = '            posts_run_obj = client.run(POSTS_RUN_ID).get()\n            posts_ds_id = posts_run_obj["defaultDatasetId"] if isinstance(posts_run_obj, dict) else posts_run_obj.default_dataset_id\n            posts_items = list(client.dataset(posts_ds_id).iterate_items())'

old2 = '                run_info = client.run(run_id).get()\n                dataset_id = run_info["defaultDatasetId"]'
new2 = '                run_obj = client.run(run_id).get()\n                dataset_id = run_obj["defaultDatasetId"] if isinstance(run_obj, dict) else run_obj.default_dataset_id'

fixed = 0
if old1 in content:
    content = content.replace(old1, new1)
    fixed += 1
    print("Fixed posts run")
else:
    print("ERROR: posts run line not found")

if old2 in content:
    content = content.replace(old2, new2)
    fixed += 1
    print("Fixed profile runs")
else:
    print("ERROR: profile run line not found")

if fixed > 0:
    open(path, "w", encoding="utf-8").write(content)
    print(f"DONE: {fixed} fixes applied")
