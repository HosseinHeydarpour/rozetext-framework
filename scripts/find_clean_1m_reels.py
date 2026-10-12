import sys, os, json, glob, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Collect all existing DB texts
existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), txt.strip()))

# Collect all json files to inspect
json_files = glob.glob('data/*.json') + glob.glob('scratch/*.json')
json_files.append(r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\candidates_32_data.json')
brain_files = glob.glob(r'C:\Users\User\.gemini\antigravity\brain\**\*.json', recursive=True)
json_files.extend(brain_files)
json_files = list(set(json_files))

print(f"Scanning {len(json_files)} json files...")

all_candidates = {}

for jf in json_files:
    if 'scripts-db.json' in jf or 'stories-db.json' in jf:
        continue
    try:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        continue
        
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        if 'scripts' in data:
            items = data['scripts']
        elif 'reels' in data:
            items = data['reels']
        elif 'items' in data:
            items = data['items']
            
    for it in items:
        if not isinstance(it, dict):
            continue
        txt = it.get('extracted_raw_text') or it.get('content') or ''
        if not txt.strip():
            continue
            
        u = it.get('source_url', '').strip()
        sc = u.rstrip('/').split('/')[-1] if u else ''
        views = str(it.get('source_views') or it.get('views') or '')
        
        # Check views 1M+
        is_1m = ('M' in views or 'میلیون' in views or '10,' in views or '1,' in views) and not ('0.' in views)
        if not is_1m:
            continue
            
        # Check lines 7..16
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if len(lines) < 7 or len(lines) > 16:
            continue
            
        # Persona filter
        page = it.get('source_page', '')
        if '@halekhoub' in page or 'halekhoub' in page:
            continue
        bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
        if any(bw in txt for bw in bad_words):
            continue
            
        # Check duplicate against published history
        res_hist = ENGINE.check_duplicate_against_history(txt, txt)
        if res_hist['is_duplicate']:
            continue
            
        # Check duplicate against DB
        c_tokens = ENGINE._normalize_persian_tokens(txt)
        c_ngrams = ENGINE._extract_ngrams(txt, 4)
        if len(c_tokens) < 4:
            continue
            
        db_dup = False
        for s_id, s_title, s_txt in existing_db_texts:
            s_tokens = ENGINE._normalize_persian_tokens(s_txt)
            overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
            s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
            common_ngrams = c_ngrams & s_ngrams
            if len(common_ngrams) >= 2 or overlap >= 0.40:
                db_dup = True
                break
        if db_dup:
            continue
            
        key = sc if sc else lines[0]
        if key not in all_candidates:
            all_candidates[key] = {
                'shortcode': sc,
                'source_url': u,
                'source_page': page or '@vahidrezakhoshbayan',
                'source_views': views,
                'title': it.get('title') or lines[0],
                'lines': len(lines),
                'content': txt,
                'archetype': it.get('archetype', 'آرکتایپ ۴: اعلام استقلال روانی و خط قرمزهای رابطه'),
                'hist_badge': res_hist['history_check_badge']
            }

print(f"\n================ TOTAL CLEAN 1M+ CANDIDATES: {len(all_candidates)} ================\n")
for k, cand in all_candidates.items():
    first_line = cand['content'].splitlines()[0]
    print(f"[{cand['shortcode']}] {cand['source_views']} | Lines: {cand['lines']} | Hook: {first_line[:40]}")
