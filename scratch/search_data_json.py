import json, glob, re, sys, os
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

data_files = glob.glob('data/hunted*.json')
print(f"Checking data files: {data_files}")

all_candidates = []

for df in data_files:
    try:
        with open(df, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        continue
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get('scripts') or data.get('reels') or data.get('items') or []
    for it in items:
        if not isinstance(it, dict):
            continue
        txt = it.get('extracted_raw_text') or it.get('content') or ''
        if not txt.strip():
            continue
        u = it.get('source_url', '')
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        code = m.group(1) if m else ''
        views = str(it.get('source_views') or it.get('views') or '')
        all_candidates.append({
            'code': code,
            'source_url': u,
            'source_page': it.get('source_page', ''),
            'source_views': views,
            'txt': txt,
            'caption': it.get('caption', ''),
            'score': it.get('score', 90),
            'archetype': it.get('archetype', '')
        })

print(f"Total raw items collected from data/*.json: {len(all_candidates)}")

# Filter
clean = []
seen = set()

for it in all_candidates:
    code = it['code']
    if not code or code in seen:
        continue
    seen.add(code)
    
    if code in used_codes or code in verified_9_codes:
        continue
        
    views = it['source_views']
    is_1m = ('M' in views or 'میلیون' in views or '1,' in views or '2,' in views or '3,' in views) and not ('0.' in views)
    if not is_1m:
        continue
        
    txt = it['txt']
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if len(lines) < 7 or len(lines) > 16:
        continue
        
    if '@halekhoub' in it['source_page'] or 'halekhoub' in it['source_page']:
        continue
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    if any(bw in txt for bw in bad_words):
        continue
        
    res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
    if res_hist['is_duplicate']:
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
        continue
        
    clean.append(it)

print(f"Clean candidates found: {len(clean)}")
for c in clean:
    print(f"\n[{c['code']}] Page: {c['source_page']} | Views: {c['source_views']}")
    print(f"URL: {c['source_url']}")
    print("Text:\n" + c['txt'])
