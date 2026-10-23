import json
import glob
import sys
import os

sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_codes = {s.get('source_url', '').split('/reel/')[-1].split('/')[0] for s in db['scripts'] if '/reel/' in s.get('source_url', '')}

# Already in verified 36
ver = json.load(open('data/verified_36_reels_clean.json', encoding='utf-8'))
selected_codes = {r['shortcode'] for r in ver}

found = []

all_files = glob.glob('data/*.json') + glob.glob('scratch/*.json')

for fpath in all_files:
    if 'scripts-db' in fpath or 'history' in fpath:
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                continue
            data = json.loads(content)
        
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for k in ['reels', 'scripts', 'items', 'candidates', 'data']:
                if k in data and isinstance(data[k], list):
                    items = data[k]
                    break
            if not items:
                # might be dict of dicts
                items = list(data.values())

        for item in items:
            if not isinstance(item, dict):
                continue
            code = item.get('shortcode') or item.get('id') or item.get('code') or ''
            if not code or len(code) < 5 or code in db_codes or code in selected_codes:
                continue
            txt = (item.get('text') or item.get('content') or item.get('extracted_raw_text') or '').strip()
            if not txt or len(txt) < 40:
                continue
            lines = [l.strip() for l in txt.split('\n') if l.strip()]
            if 7 <= len(lines) <= 16:
                res = engine.check(txt)
                if not res['is_duplicate'] and res['similarity_score'] < 35:
                    views = item.get('views') or item.get('view_count') or item.get('source_views') or '—'
                    author = item.get('author') or item.get('owner_username') or item.get('source_page') or '—'
                    url = item.get('url') or item.get('source_url') or f'https://www.instagram.com/reel/{code}/'
                    found.append({
                        'code': code,
                        'author': author,
                        'views': views,
                        'lines': len(lines),
                        'sim': res['similarity_score'],
                        'url': url,
                        'text': txt,
                        'file': fpath
                    })
    except Exception:
        pass

print(f"Total discovered candidate reels: {len(found)}")
# Deduplicate by code
unique = {}
for r in found:
    if r['code'] not in unique or r['sim'] < unique[r['code']]['sim']:
        unique[r['code']] = r

print(f"Unique candidate reels: {len(unique)}")
for code, r in sorted(unique.items(), key=lambda x: (x[1]['sim'], -x[1]['lines']))[:20]:
    print(f"[{r['code']}] {r['author']:<20} | Views: {r['views']:<6} | Lines: {r['lines']:2d} | Sim: {r['sim']:4.1f}% | File: {r['file']}")
    print(f"   Line 1: {r['text'].splitlines()[0]}")
