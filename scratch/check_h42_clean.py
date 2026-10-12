import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from server import ENGINE

with open('data/hunted-42-reels-batch.json', 'r', encoding='utf-8') as f:
    h42 = json.load(f)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))
db_codes = set()
for u in db_urls:
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    if m:
        db_codes.add(m.group(1))

verified_9_codes = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DNTYt15oqYj', 'DZSr1vMN1mr',
    'DPjI0mTCIPs', 'DKm6Qn6I9vQ', 'DQHm9z6CMeL', 'DPRj9ddCF5T', 'DbyY0F7tmAn'
}

print(f"Total in h42: {len(h42)}")
for idx, r in enumerate(h42, 1):
    t = r.get('content', '')
    dup = ENGINE.check_duplicate_against_history(t, t)
    u = r.get('source_url', '').strip()
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    sc = m.group(1) if m else ''
    is_in_db = sc in db_codes or u in db_urls
    is_in_9 = sc in verified_9_codes
    
    views = r.get('source_views', '')
    is_1m = ('M' in views or 'میلیون' in views or '1,' in views or '2,' in views or '3,' in views) and not ('0.' in views)
    
    if not dup['is_duplicate'] and not is_in_db and not is_in_9 and is_1m:
        print(f"\n★ FOUND CLEAN CANDIDATE! #{idx} [{sc}] ({views})")
        print(f"Title: {r.get('title')}")
        print(f"URL: {u}")
        print(f"Text:\n{t}")
