import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/hunted-42-reels-batch.json", "r", encoding="utf-8") as f:
    batch = json.load(f)

for idx in [25, 26, 28, 30]:
    it = batch[idx]
    print(f"=== Item {idx}: {it.get('title')} ({it.get('source_views')}) ===")
    print("Content:\n" + it.get("content", ""))
    print("-----------------------------------------")
