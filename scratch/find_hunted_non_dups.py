import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c)

files = glob.glob('data/hunted*.json')
all_items = []
seen_codes = set()

for fp in files:
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            items = json.load(f)
            if not isinstance(items, list):
                continue
            for it in items:
                u = it.get('source_url', '')
                m = re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', u)
                if not m:
                    continue
                code = m[0]
                if code in db_codes or code in seen_codes:
                    continue
                seen_codes.add(code)
                
                v_str = str(it.get('source_views', ''))
                # check if 1M+
                is_million = False
                if 'M' in v_str or 'm' in v_str or 'میلیون' in v_str:
                    is_million = True
                else:
                    digits = re.findall(r'[\d,]+', v_str)
                    for d in digits:
                        nd = d.replace(',', '')
                        if nd.isdigit() and int(nd) >= 1000000:
                            is_million = True
                            break
                if not is_million:
                    continue
                
                raw = it.get('extracted_raw_text', '') or it.get('content', '')
                lines = [l.strip() for l in raw.split('\n') if l.strip()]
                if not (6 <= len(lines) <= 18):
                    continue
                
                dup = engine.check_duplicate_against_history(raw, raw)
                if not dup['is_duplicate']:
                    all_items.append({
                        'code': code,
                        'url': u,
                        'page': it.get('source_page', ''),
                        'views': v_str,
                        'title': it.get('title', ''),
                        'archetype': it.get('archetype', ''),
                        'lines_count': len(lines),
                        'text': raw,
                        'caption': it.get('caption', ''),
                        'sim': dup['similarity_score']
                    })
    except Exception as e:
        print(f"Error {fp}: {e}")

print(f"Found {len(all_items)} non-duplicate 1M+ reels in data/hunted*.json:")
for i, it in enumerate(all_items):
    print(f"{i+1}. [{it['views']}] {it['code']} ({it['page']}) -> Sim: {it['sim']}% | Title: {it['title'][:40]}")
