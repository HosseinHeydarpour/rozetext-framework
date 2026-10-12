import os, sys, glob, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))
existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append(txt.strip())

fbee_dir = r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c'
files = glob.glob(os.path.join(fbee_dir, '*.json'))

print(f"Scanning files in {fbee_dir}:")
for fpath in files:
    fname = os.path.basename(fpath)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {fname}: {e}")
        continue
        
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for k in ['scripts', 'reels', 'candidates', 'items', 'data']:
            if k in data and isinstance(data[k], list):
                items = data[k]
                break
        if not items and isinstance(data, dict):
            # Maybe it's a dict of items
            items = list(data.values()) if all(isinstance(v, dict) for v in data.values()) else [data]
            
    print(f"\n--- {fname} (found {len(items)} items) ---")
    
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            continue
        txt = it.get('extracted_raw_text') or it.get('content') or it.get('text') or ''
        if not txt.strip():
            continue
            
        u = it.get('source_url') or it.get('url') or it.get('link') or ''
        views = str(it.get('source_views') or it.get('views') or it.get('view_count') or '')
        page = it.get('source_page') or it.get('page') or ''
        
        # Check views 1M+
        is_1m = ('M' in views or 'میلیون' in views or any(k in views for k in ['1,', '2,', '3,', '4,', '5,', '6,', '7,', '8,', '9,', '10,'])) and not any(k in views for k in ['0.', '۰٫'])
        
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        line_count = len(lines)
        
        # Check duplicate against published history
        res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
        
        # Check duplicate against DB
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
                
        in_db = u in db_urls or any(re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u) and re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u).group(1) in du for du in db_urls) if u else False
        
        # Bad words & persona
        bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
        has_bad = any(bw in txt for bw in bad_words) or '@halekhoub' in page or 'halekhoub' in page
        
        status = []
        if is_1m: status.append("1M+")
        else: status.append(f"Views: {views[:10]}")
        status.append(f"{line_count}L")
        if in_db: status.append("InDB")
        if db_dup: status.append("DBDup")
        if res_hist['is_duplicate']: status.append(f"HistDup({res_hist['similarity_score']:.0f}%)")
        if has_bad: status.append("BadPersona")
        
        if is_1m and 7 <= line_count <= 16 and not in_db and not db_dup and not res_hist['is_duplicate'] and not has_bad:
            print(f"  >>> [MATCH #{idx}] {u} | Views: {views} | Lines: {line_count} | Page: {page}")
            print(f"      Hook: {lines[0]}")
            print(f"      Full Text:\n{txt}\n")
        else:
            # print compact status
            pass
