import json
import glob
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

for fpath in glob.glob('downloads/*_high*.json'):
    with open(fpath, encoding='utf-8') as f:
        data = json.load(f)
    print(f"\n=== {os.path.basename(fpath)}: {len(data)} items ===")
    for item in data:
        views = item.get("views", 0)
        code = item.get("code")
        vstr = item.get("views_str", "")
        if views >= 400000:
            print(f"  {code} | {vstr} | {views}")
