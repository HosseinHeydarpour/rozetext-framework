import json
import sys
import re
sys.stdout.reconfigure(encoding='utf-8')
from server import ENGINE

with open("data/hunted-42-reels-batch-verified.json", "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Loaded {len(items)} items from data/hunted-42-reels-batch-verified.json")
assert len(items) == 42, f"Expected 42 items, got {len(items)}"

all_lines = []
errors = []

# Intra-batch duplicate check
seen_4grams = {}

for idx, item in enumerate(items):
    content = item.get("content", "").strip()
    raw = item.get("extracted_raw_text", "").strip()
    source_url = item.get("source_url", "")
    source_page = item.get("source_page", "")
    source_views = item.get("source_views", "")
    title = item.get("title", "")
    score = item.get("score", 0)

    # 1. Direct raw text check
    if content != raw:
        errors.append(f"Item #{idx+1} ({title}): content does not match extracted_raw_text!")

    # 2. Line count
    lines = [l for l in content.split("\n") if l.strip()]
    if not (7 <= len(lines) <= 16):
        errors.append(f"Item #{idx+1} ({title}): line count is {len(lines)} (must be 7-16)!")

    # 3. View count check
    if not any(k in source_views for k in ["M", "میلیون", "000,000"]):
        errors.append(f"Item #{idx+1} ({title}): views '{source_views}' might not be >= 1M!")

    # 4. Check duplicate against history #1 to #269
    dup = ENGINE.check_duplicate_against_history(content, content)
    if dup["is_duplicate"]:
        errors.append(f"Item #{idx+1} ({title}): DUPLICATE with history! {dup}")

    # 5. Intra-batch 4-gram duplicate check
    words = re.findall(r'[\w\u0600-\u06FF]+', content)
    for i in range(len(words) - 3):
        ngram = " ".join(words[i:i+4])
        if ngram in seen_4grams:
            if seen_4grams[ngram] != idx:
                errors.append(f"Item #{idx+1} ({title}): shares 4-gram '{ngram}' with item #{seen_4grams[ngram]+1}!")
        else:
            seen_4grams[ngram] = idx

if errors:
    print(f"FAILED with {len(errors)} errors:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
else:
    print("SUCCESS! All 42 reels passed 100% of strict quality, formatting, view count, and deduplication checks!")
