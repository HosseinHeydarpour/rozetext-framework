import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Fixes for case-sensitive shortcodes
fixes = [
    ('DKC2DqwiyM_', 'DKC2DQwIyM_'),
    ('DMVWoiaor6o', 'DMvWoiaor6o'),
    ('DKm6Qn6I9VQ', 'DKm6Qn6I9vQ')
]

# 1. Fix in scripts-db.json
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

fixed_count = 0
for s in db['scripts']:
    url = s.get('source_url', '')
    for old_code, new_code in fixes:
        if old_code in url:
            s['source_url'] = url.replace(old_code, new_code)
            print(f"Fixed DB script {s['id']}: {old_code} -> {new_code}")
            fixed_count += 1

with open('data/scripts-db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# 2. Fix in data/hunted-42-reels-batch-verified.json
with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

for b in batch:
    url = b.get('source_url', '')
    for old_code, new_code in fixes:
        if old_code in url:
            b['source_url'] = url.replace(old_code, new_code)
            print(f"Fixed batch item: {old_code} -> {new_code}")

with open('data/hunted-42-reels-batch-verified.json', 'w', encoding='utf-8') as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print(f"Done! Successfully updated {fixed_count} records.")
