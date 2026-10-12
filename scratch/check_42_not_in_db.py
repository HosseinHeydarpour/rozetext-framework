import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set()
db_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        db_urls.add(u)
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            db_codes.add(m.group(1))

print(f"Total db scripts: {len(db.get('scripts', []))}")
print(f"Total db codes: {len(db_codes)}")

not_in_db = []
for i, item in enumerate(batch, 1):
    u = item.get('source_url', '')
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    code = m.group(1) if m else ''
    if code not in db_codes and u not in db_urls:
        not_in_db.append((i, code, item))

print(f"\nItems from 42-batch NOT anywhere in scripts-db.json: {len(not_in_db)}")
for i, code, item in not_in_db:
    views = item.get('source_views')
    txt = item.get('extracted_raw_text') or item.get('content') or ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    print(f"#{i:02d} [{code}] ({views}) - {item.get('title')} | Lines: {len(lines)}")
