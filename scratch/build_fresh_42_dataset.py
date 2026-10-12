import json
import sys
import re

sys.path.insert(0, ".")
from server import PublisherEngine

sys.stdout.reconfigure(encoding="utf-8")

engine = PublisherEngine()

# 1. Load the 19 unique reels from earlier batch
with open("data/hunted-42-reels-batch.json", "r", encoding="utf-8") as f:
    orig_batch = json.load(f)

saved_unique_19 = []
for item in orig_batch:
    res = engine.check_duplicate_against_history(item.get("content", ""), item.get("extracted_raw_text", ""))
    if not res["is_duplicate"]:
        saved_unique_19.append(item)

print(f"Loaded {len(saved_unique_19)} unique reels from original batch.")

# Check count needed
needed = 42 - len(saved_unique_19)
print(f"Need {needed} more reels to make 42.")
