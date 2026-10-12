import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

used_codes = set()
existing_db_texts = []
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append(txt.strip())

verified_9_codes = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DNTYt15oqYj', 'DZSr1vMN1mr',
    'DPjI0mTCIPs', 'DKm6Qn6I9vQ', 'DQHm9z6CMeL', 'DPRj9ddCF5T', 'DbyY0F7tmAn'
}

with open(r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\candidates_32_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total items in candidates_32_data: {len(data)}")
for i, it in enumerate(data):
    u = it.get('source_url') or it.get('url') or ''
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    sc = m.group(1) if m else it.get('id', '')
    views = str(it.get('source_views') or it.get('views') or '')
    txt = it.get('extracted_raw_text') or it.get('content') or it.get('text') or ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    hook = lines[0] if lines else txt[:40]
    
    in_db = sc in used_codes
    in_9 = sc in verified_9_codes
    
    # check history
    res_hist = ENGINE.check_duplicate_against_history(hook, txt) if txt else {'is_duplicate': False}
    
    print(f"[{i+1}] {sc} | {views} | Lines: {len(lines)} | in_db={in_db} | in_9={in_9} | hist_dup={res_hist['is_duplicate']}")
    print(f"    Hook: {hook}")
