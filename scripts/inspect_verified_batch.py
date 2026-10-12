import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

print(f"Total verified hunted reels: {len(batch)}\n")
for i in range(18):
    item = batch[i]
    print(f"#{i+1} [{item.get('archetype', '')[:12]}] {item.get('title')}")
    print(f"   Views: {item.get('source_views')} | URL: {item.get('source_url')}")
    print(f"   Score: {item.get('score')} | Hook: {item.get('hook')}")
    print("-" * 50)
