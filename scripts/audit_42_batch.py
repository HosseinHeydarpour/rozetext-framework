import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

print(f'Total reels in 42-batch: {len(batch)}')

candidates = []
for i, item in enumerate(batch, 1):
    txt = (item.get('extracted_raw_text') or item.get('content') or '').strip()
    u = item.get('source_url', '')
    views = str(item.get('source_views', ''))
    code = u.rstrip('/').split('/')[-1] if u else ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    
    is_1m = ('M' in views or 'میلیون' in views or '10,' in views or '1,' in views) and not ('0.' in views)
    in_db = code in db_codes
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    max_dbsim = 0
    for dbt in db_texts:
        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
        sim = len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens)))
        if sim > max_dbsim:
            max_dbsim = sim
            
    is_dup = hist['is_duplicate']
    score = hist['similarity_score']
    is_clean = is_1m and (not in_db) and (not is_dup) and (max_dbsim < 0.40) and (7 <= len(lines) <= 16)
    
    if is_1m:
        print(f"#{i} [{code}] ({views[:15]}) | Lines: {len(lines)} | InDB: {in_db} | HistDup: {is_dup} ({score:.1f}%) | DBSim: {max_dbsim:.1%} | CLEAN: {is_clean}")
        if is_clean:
            candidates.append(item)

print(f'\nTotal Clean 1M+ Candidates in 42-batch: {len(candidates)}')
for c in candidates:
    print('Clean:', c.get('source_url'), c.get('title')[:40])
