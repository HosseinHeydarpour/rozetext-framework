import json, re

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Extract all shortcodes used in scripts-db
used_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))

with open('scratch/reels_51.json', 'r', encoding='utf-8') as f:
    reels = json.load(f)

unused = []
for r in reels:
    rid = r['id']
    views = r['views']
    if 'M' in views and not '0.' in views:
        if rid not in used_codes:
            unused.append(r)

print(f"Total unused 1M+ reels from this list: {len(unused)}")
for u in unused:
    print(f"- {u['id']}: {u['views']} ({u['href']})")
