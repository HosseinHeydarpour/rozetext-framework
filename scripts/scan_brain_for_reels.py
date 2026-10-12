import os, glob, json, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

brain_dir = r'C:\Users\User\.gemini\antigravity\brain'

found_clean = []
seen_codes = set()

for root, dirs, files in os.walk(brain_dir):
    if '.system_generated' in root:
        continue
    for file in files:
        if file.endswith('.json'):
            fpath = os.path.join(root, file)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                items = data if isinstance(data, list) else (data.get('scripts') or data.get('reels') or data.get('candidates') or data.get('items') or [])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    txt = (item.get('extracted_raw_text') or item.get('content') or item.get('text') or '').strip()
                    views = str(item.get('source_views') or item.get('views') or '')
                    u = item.get('source_url') or item.get('url') or ''
                    code = u.rstrip('/').split('/')[-1] if u else ''
                    if not ('M' in views or '1,' in views or 'میلیون' in views):
                        continue
                    if '0.' in views:
                        continue
                    if code and (code in db_codes or code in seen_codes):
                        continue
                    lines = [l.strip() for l in txt.splitlines() if l.strip()]
                    if not (7 <= len(lines) <= 16):
                        continue
                    hist = ENGINE.check_duplicate_against_history(txt, txt)
                    if hist['is_duplicate']:
                        continue
                    c_tokens = ENGINE._normalize_persian_tokens(txt)
                    dup_db = False
                    for dbt in db_texts:
                        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
                        if len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens))) >= 0.40:
                            dup_db = True
                            break
                    if dup_db:
                        continue
                    if code:
                        seen_codes.add(code)
                    found_clean.append({
                        'code': code,
                        'views': views,
                        'lines': len(lines),
                        'hook': lines[0],
                        'url': u,
                        'text': txt,
                        'file': fpath,
                        'item': item,
                        'sim': hist['similarity_score']
                    })
            except Exception:
                pass

print(f'Total clean 1M+ found in brain: {len(found_clean)}')
for fc in found_clean:
    print(f"[{fc['code']}] {fc['views']} | Lines: {fc['lines']} | Sim: {fc['sim']:.1f}%")
    print(f"  Hook: {fc['hook']}")
    print(f"  File: {fc['file']}")
    print("-" * 50)
