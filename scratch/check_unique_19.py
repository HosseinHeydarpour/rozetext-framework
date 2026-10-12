import json
import sys
sys.path.insert(0, ".")
from server import PublisherEngine

sys.stdout.reconfigure(encoding="utf-8")

with open("data/hunted-42-reels-batch.json", "r", encoding="utf-8") as f:
    batch = json.load(f)

engine = PublisherEngine()
unique_items = []
for idx, item in enumerate(batch):
    content = item.get("content", "")
    raw = item.get("extracted_raw_text", "")
    res = engine.check_duplicate_against_history(content, raw)
    if not res["is_duplicate"]:
        unique_items.append((idx, item))

print(f"Total unique non-duplicate reels available: {len(unique_items)}")
for i, (idx, item) in enumerate(unique_items):
    views = item.get("source_views", "")[:25]
    page = item.get("source_page", "")
    url = item.get("source_url", "")
    title = item.get("title", "")[:50]
    print(f"{i+1}. [Orig #{idx}] {page} | {views} | {title} | {url}")
