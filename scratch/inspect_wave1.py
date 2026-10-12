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

with open(r'C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total items in batch2_wave1_29: {len(items)}")

clean = []
for it in items:
    sc = it.get('shortcode') or ''
    u = it.get('url') or ''
    if not sc and u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        sc = m.group(1) if m else ''
        
    views = str(it.get('views') or '')
    is_1m = ('M' in views or 'میلیون' in views or '1,' in views or '2,' in views or '3,' in views) and not ('0.' in views)
    
    txt = it.get('video_text') or ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    
    account = it.get('account') or ''
    
    print(f"\nItem: {sc} | Views: {views} | Lines: {len(lines)} | is_1m={is_1m} | in_used={sc in used_codes} | in_9={sc in verified_9_codes}")
    if lines:
        print(f"Hook: {lines[0]}")
        print("Text snippet:", " / ".join(lines[:3]))
    
    if not is_1m or sc in used_codes or sc in verified_9_codes:
        continue
    if len(lines) < 7 or len(lines) > 16:
        continue
    if '@halekhoub' in account or 'halekhoub' in account:
        continue
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    if any(bw in txt for bw in bad_words):
        continue
        
    res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
    if res_hist['is_duplicate']:
        print(f"--> Dup of history: Reel #{res_hist.get('duplicate_of_reel')} ({res_hist['similarity_score']}%)")
        continue
        
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    db_dup = False
    for s_txt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(s_txt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
        if len(c_ngrams & s_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            break
    if db_dup:
        print("--> Dup of scripts-db")
        continue
        
    clean.append((sc, it))

print(f"\n================ VALID CLEAN 1M+ CANDIDATES: {len(clean)} ================")
for sc, it in clean:
    print(f"[{sc}] {it['views']} | @{it['account']}")
    print(it['video_text'])
