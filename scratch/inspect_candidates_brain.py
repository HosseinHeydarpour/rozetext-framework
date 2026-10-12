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

files = [
    r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\candidates_32_data.json',
    r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\new_top_50_reels.json',
    r'C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json'
]

clean_candidates = []
seen = set()

for fp in files:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get('scripts') or data.get('reels') or data.get('items') or data.get('candidates') or []
        if not items and 'id' in data:
            items = [data]
            
    print(f"File {os.path.basename(fp)}: {len(items)} items")
    for it in items:
        u = it.get('source_url') or it.get('url') or ''
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        code = m.group(1) if m else it.get('id', '')
        if not code or code in seen:
            continue
        seen.add(code)
        
        if code in used_codes or code in verified_9_codes:
            continue
            
        views = str(it.get('source_views') or it.get('views') or '')
        # Must be 1M+
        is_1m = ('M' in views or 'میلیون' in views or '1,' in views or '2,' in views or '3,' in views or '1.' in views) and not ('0.' in views)
        if not is_1m:
            continue
            
        txt = it.get('extracted_raw_text') or it.get('content') or it.get('text') or ''
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if len(lines) < 7 or len(lines) > 16:
            continue
            
        page = it.get('source_page') or it.get('page') or ''
        if '@halekhoub' in page or 'halekhoub' in page:
            continue
        bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
        if any(bw in txt for bw in bad_words):
            continue
            
        res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
        if res_hist['is_duplicate']:
            print(f"Skip {code}: dup of history Reel #{res_hist.get('duplicate_of_reel')} ({res_hist['similarity_score']}%)")
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
            print(f"Skip {code}: dup of scripts-db")
            continue
            
        clean_candidates.append({
            'code': code,
            'source_url': u or f'https://www.instagram.com/reel/{code}/',
            'source_page': page,
            'source_views': views,
            'lines': lines,
            'txt': txt,
            'caption': it.get('caption', ''),
            'file': os.path.basename(fp)
        })

print(f"\n================ TOTAL CLEAN 1M+ CANDIDATES: {len(clean_candidates)} ================")
for c in clean_candidates:
    print(f"\n[{c['code']}] Page: {c['source_page']} | Views: {c['source_views']} | Lines: {len(c['lines'])} | From: {c['file']}")
    print(f"URL: {c['source_url']}")
    print(f"Hook: {c['lines'][0]}")
    print("Text:\n" + c['txt'])
