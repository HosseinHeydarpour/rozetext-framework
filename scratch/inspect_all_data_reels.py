import json
import glob
import sys
sys.path.insert(0, ".")
from server import PublisherEngine

sys.stdout.reconfigure(encoding="utf-8")

engine = PublisherEngine()

all_reels = []
seen_urls = set()

for fpath in glob.glob("data/*.json"):
    if "scripts-db" in fpath:
        continue
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            items = json.load(f)
            if isinstance(items, list):
                for it in items:
                    url = it.get("source_url")
                    c = it.get("content", "").strip()
                    if c and url not in seen_urls:
                        seen_urls.add(url)
                        all_reels.append(it)
    except Exception as e:
        print(f"Error {fpath}: {e}")

print(f"Total distinct reels across all json files: {len(all_reels)}")

# Check duplicate against published history (269 reels)
non_dup_reels = []
for it in all_reels:
    c = it.get("content", "")
    raw = it.get("extracted_raw_text", "")
    res = engine.check_duplicate_against_history(c, raw)
    if not res["is_duplicate"]:
        non_dup_reels.append(it)

print(f"Non-duplicate reels against history: {len(non_dup_reels)}")
for i, r in enumerate(non_dup_reels):
    print(f"{i+1}. [{r.get('source_page')}] {str(r.get('source_views'))[:25]} | {r.get('title')[:40]} | lines: {len(r.get('content','').splitlines())} | {r.get('source_url')}")
