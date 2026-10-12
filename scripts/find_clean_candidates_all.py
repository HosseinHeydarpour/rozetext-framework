import glob, json, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

print(f'DB scripts count: {len(db["scripts"])}, DB codes: {len(db_codes)}')

candidates = []
for fpath in glob.glob('scratch/*.json') + glob.glob('data/*.json') + glob.glob('scripts/*.py') + glob.glob('scratch/*.py'):
    if 'scripts-db.json' in fpath or 'stories-db.json' in fpath:
        continue
    try:
        if fpath.endswith('.json'):
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items = data if isinstance(data, list) else (data.get('scripts') or data.get('reels') or data.get('items') or [])
            for it in items:
                if isinstance(it, dict):
                    candidates.append((fpath, it))
    except Exception as e:
        pass

print(f'Total candidate items loaded: {len(candidates)}')

clean_1m = []
for fpath, it in candidates:
    txt = (it.get('extracted_raw_text') or it.get('content') or '').strip()
    u = it.get('source_url') or it.get('url') or ''
    views = str(it.get('source_views') or it.get('views') or '')
    code = u.rstrip('/').split('/')[-1] if u else ''
    
    if not ('M' in views or '1,' in views or 'میلیون' in views):
        continue
    if '0.' in views:
        continue
    if code in db_codes:
        continue
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if not (7 <= len(lines) <= 16):
        continue
        
    # Check history duplicate
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    if hist['is_duplicate']:
        continue
        
    # Check DB duplicate
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    db_dup = False
    for dbt in db_texts:
        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
        if len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens))) >= 0.40:
            db_dup = True
            break
    if db_dup:
        continue
        
    clean_1m.append({
        'code': code,
        'views': views,
        'lines': len(lines),
        'hook': lines[0],
        'url': u,
        'page': it.get('source_page') or it.get('page') or '',
        'text': txt,
        'fpath': fpath,
        'sim': hist['similarity_score']
    })

unique_clean = {}
for c in clean_1m:
    if c['code'] not in unique_clean:
        unique_clean[c['code']] = c

print(f'\n=== FOUND {len(unique_clean)} CLEAN 1M+ CANDIDATES NOT IN DB OR HISTORY ===\n')
for code, c in unique_clean.items():
    print(f"[{code}] {c['views']} | Lines: {c['lines']} | Sim: {c['sim']:.1f}% | Page: {c['page']}")
    print(f"  Hook: {c['hook']}")
    print(f"  File: {c['fpath']}")
    print("-" * 50)
