import os, glob, json, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

found_candidates = []
seen_urls = set()

for root, dirs, files in os.walk('.'):
    if '.git' in root or '.venv' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.json') and file not in ['scripts-db.json', 'stories-db.json', 'package.json', 'package-lock.json']:
            fpath = os.path.join(root, file)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                items = data if isinstance(data, list) else (data.get('scripts') or data.get('reels') or data.get('items') or [])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    txt = item.get('extracted_raw_text') or item.get('content') or ''
                    views = str(item.get('source_views') or item.get('views') or '')
                    u = item.get('source_url', '')
                    if not ('M' in views or '1,' in views or 'میلیون' in views):
                        continue
                    if '0.' in views:
                        continue
                    lines = [l.strip() for l in txt.splitlines() if l.strip()]
                    if not (7 <= len(lines) <= 16):
                        continue
                    if u and u in seen_urls:
                        continue
                    # Check history duplicate
                    res = ENGINE.check_duplicate_against_history(txt, txt)
                    if res['is_duplicate']:
                        continue
                    # Check DB duplicate
                    c_tokens = ENGINE._normalize_persian_tokens(txt)
                    dup_db = False
                    for dbt in db_texts:
                        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
                        if len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens))) >= 0.40:
                            dup_db = True
                            break
                    if dup_db:
                        continue
                    if u:
                        seen_urls.add(u)
                    found_candidates.append({
                        'file': fpath,
                        'url': u,
                        'views': views,
                        'lines': len(lines),
                        'hook': lines[0],
                        'text': txt,
                        'raw': item
                    })
            except Exception:
                pass

print(f'Total clean 1M+ candidates found across workspace: {len(found_candidates)}')
for fc in found_candidates:
    v = fc['views']
    l = fc['lines']
    h = fc['hook']
    u = fc['url']
    print(f"- [{v}] ({l} lines): {h} -> {u}")
