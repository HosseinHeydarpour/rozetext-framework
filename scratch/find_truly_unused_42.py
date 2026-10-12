import json
import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from server import PublisherEngine
engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

all_db_urls = set()
all_db_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        all_db_urls.add(u.strip())
        code = u.strip().rstrip('/').split('/')[-1]
        all_db_codes.add(code)
    # also check extra_notes
    notes = s.get('extra_notes', '')
    for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', notes):
        all_db_codes.add(c)

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

print(f"Total batch items: {len(batch)}")
print(f"Total DB codes: {len(all_db_codes)}")

truly_unused = []

for idx, item in enumerate(batch, 1):
    u = item.get('source_url', '').strip()
    code = u.rstrip('/').split('/')[-1] if '/reel/' in u else ''
    
    in_db = (u in all_db_urls) or (code in all_db_codes)
    
    c = item.get('content') or item.get('extracted_raw_text') or ''
    lines = [l.strip() for l in c.splitlines() if l.strip()]
    
    dup = engine.check_duplicate_against_history(c, c)
    
    views_str = item.get('source_views', '')
    
    if not in_db and not dup['is_duplicate'] and len(lines) >= 7:
        truly_unused.append({
            'idx': idx,
            'code': code,
            'url': u,
            'page': item.get('source_page'),
            'views': views_str,
            'lines': len(lines),
            'title': item.get('title'),
            'hook': lines[0] if lines else '',
            'sim': dup['similarity_score'],
            'item': item
        })
    else:
        status_reasons = []
        if in_db: status_reasons.append("IN_DB")
        if dup['is_duplicate']: status_reasons.append(f"DUP_HIST({dup['similarity_score']:.1f}%_Reel#{dup['duplicate_of_reel']})")
        if len(lines) < 7: status_reasons.append(f"SHORT({len(lines)}L)")
        print(f"#{idx:02d} [{', '.join(status_reasons)}] {code} | Views: {views_str}")

print(f"\n================ TRULY UNUSED & VALID IN 42-BATCH: {len(truly_unused)} ================")
for t in truly_unused:
    print(f"#{t['idx']:02d} [{t['views']}] {t['code']} ({t['page']}) | Lines: {t['lines']} | Sim: {t['sim']:.1f}%")
    print(f"   Hook: {t['hook']}")
