import json
import glob
import sys
sys.path.insert(0, ".")
from server import PublisherEngine

sys.stdout.reconfigure(encoding="utf-8")

engine = PublisherEngine()

all_files = glob.glob("data/hunted-*.json")
print("Found files:", all_files)

candidates = []
seen_content = set()

for fpath in all_files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    c = item.get("content", "").strip()
                    if c and c not in seen_content:
                        seen_content.add(c)
                        candidates.append((fpath, item))
    except Exception as e:
        print(f"Error loading {fpath}: {e}")

print(f"Total unique candidates loaded: {len(candidates)}")

valid_fresh = []
for fpath, item in candidates:
    content = item.get("content", "")
    raw = item.get("extracted_raw_text", "")
    res = engine.check_duplicate_against_history(content, raw)
    if not res["is_duplicate"]:
        views_str = str(item.get("source_views", ""))
        valid_fresh.append({
            "source_file": fpath,
            "title": item.get("title", ""),
            "page": item.get("source_page", ""),
            "views": views_str,
            "url": item.get("source_url", ""),
            "item": item
        })

print(f"Candidates that are 100% NOT in published history (269 reels): {len(valid_fresh)}")
for i, vf in enumerate(valid_fresh):
    print(f"{i+1}. [{vf['page']}] {vf['views'][:25]} | {vf['title'][:40]} | {vf['url']}")
