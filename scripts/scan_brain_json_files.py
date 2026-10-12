import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

base_dir = r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c'
json_files = ['candidates_32_data.json', 'verify_27_data.json', 'verify_4_data.json']

qualifying = []

for jf in json_files:
    p = os.path.join(base_dir, jf)
    if not os.path.exists(p):
        continue
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    items = data if isinstance(data, list) else (data.get('items') or data.get('reels') or data.get('candidates') or [])
    print(f'{jf}: {len(items)} items')
    for it in items:
        u = it.get('source_url') or it.get('url') or ''
        code = u.rstrip('/').split('/')[-1] if u else it.get('code', '')
        views = str(it.get('source_views') or it.get('views') or '')
        txt = (it.get('extracted_raw_text') or it.get('content') or it.get('text') or '').strip()
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        
        is_1m = ('M' in views or '1,' in views or '2,' in views or '3,' in views or '4,' in views or '5,' in views or 'میلیون' in views) and not ('0.' in views)
        if not is_1m or code in db_codes or not (7 <= len(lines) <= 16):
            continue
            
        hist = ENGINE.check_duplicate_against_history(txt, txt)
        if hist['is_duplicate']:
            continue
            
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
            
        qualifying.append({
            'code': code,
            'url': u or f'https://www.instagram.com/reel/{code}/',
            'views': views,
            'page': it.get('source_page') or it.get('page') or it.get('account') or '',
            'lines': len(lines),
            'hook': lines[0],
            'text': txt,
            'hist_sim': hist['similarity_score'],
            'db_sim': max_dbsim,
            'file': jf
        })

print(f'\n=== FOUND {len(qualifying)} QUALIFYING 1M+ REELS ===\n')
seen = set()
for q in qualifying:
    if q['code'] not in seen:
        seen.add(q['code'])
        print(f"[{q['code']}] {q['page']} ({q['views']}) | Lines: {q['lines']} | Hist: {q['hist_sim']:.1f}% | DB: {q['db_sim']:.1%} | File: {q['file']}")
        print(f"Hook: {q['hook']}")
        print(q['text'])
        print('-'*50)
