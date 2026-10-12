import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

print(f'DB has {len(db["scripts"])} scripts, {len(db_codes)} codes')

files = [
    'data/hunted-42-reels-batch-verified.json',
    'data/hunted-42-reels-batch.json',
    'data/hunted-batch-2026-09-29-4days.json',
    'data/hunted-batch-2026-10-03.json',
    'data/hunted-batch-2026-09-28.json'
]
all_candidates = []

for fn in files:
    if not os.path.exists(fn):
        continue
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data if isinstance(data, list) else (data.get('scripts') or data.get('reels') or [])
    for it in items:
        all_candidates.append((fn, it))

print(f'Loaded {len(all_candidates)} items across batch files')

qualifying = []
seen_codes = set()

for fn, it in all_candidates:
    u = it.get('source_url') or it.get('url') or ''
    code = u.rstrip('/').split('/')[-1] if u else ''
    if not code or code in seen_codes:
        continue
    views = str(it.get('source_views') or it.get('views') or '')
    is_1m = ('M' in views or '1,' in views or '2,' in views or '3,' in views or 'میلیون' in views) and not ('0.' in views)
    if not is_1m:
        continue
    if code in db_codes:
        continue
    txt = (it.get('extracted_raw_text') or it.get('content') or '').strip()
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if not (7 <= len(lines) <= 16):
        continue
    
    # history check
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    if hist['is_duplicate']:
        continue
        
    # db check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    db_dup = False
    max_dbsim = 0
    for dbt in db_texts:
        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
        sim = len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens)))
        if sim > max_dbsim:
            max_dbsim = sim
        if sim >= 0.40:
            db_dup = True
            break
    if db_dup:
        continue
        
    seen_codes.add(code)
    qualifying.append({
        'code': code,
        'url': u,
        'views': views,
        'page': it.get('source_page') or it.get('page') or '',
        'lines': len(lines),
        'hook': lines[0],
        'text': txt,
        'hist_sim': hist['similarity_score'],
        'db_sim': max_dbsim,
        'item': it
    })

print(f'\n=== FOUND {len(qualifying)} QUALIFYING 1M+ REELS ===\n')
for q in qualifying:
    print(f"[{q['code']}] {q['page']} | Views: {q['views']} | Lines: {q['lines']} | HistSim: {q['hist_sim']:.1f}% | DBSim: {q['db_sim']:.1%}")
    print(f"Hook: {q['hook']}")
    print(q['text'])
    print('-'*50)
