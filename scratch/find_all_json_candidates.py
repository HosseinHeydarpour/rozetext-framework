import json
import glob
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c.lower())

candidates = []
seen = set()

for fp in glob.glob('data/*.json'):
    if 'scripts-db' in fp or 'stories-db' in fp:
        continue
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                continue
            for item in data:
                u = item.get('source_url', '')
                m = re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', u)
                if not m:
                    continue
                code = m[0]
                if code.lower() in db_codes or code.lower() in seen:
                    continue
                seen.add(code.lower())
                
                v_str = str(item.get('source_views', ''))
                # million check
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
                
                raw = item.get('extracted_raw_text', '') or item.get('content', '')
                lines = [l.strip() for l in raw.split('\n') if l.strip()]
                if not (7 <= len(lines) <= 16):
                    continue
                
                # Check blacklist
                page = item.get('source_page', '')
                if 'halekhoub' in page.lower():
                    continue
                
                # Check poets
                if 'مولانا' in raw or 'شمس' in raw:
                    continue
                
                dup = engine.check_duplicate_against_history(raw, raw)
                if dup['is_duplicate']:
                    continue
                
                candidates.append({
                    'code': code,
                    'url': u,
                    'page': page,
                    'views': v_str,
                    'title': item.get('title', ''),
                    'archetype': item.get('archetype', ''),
                    'lines_count': len(lines),
                    'text': raw,
                    'caption': item.get('caption', ''),
                    'sim': dup['similarity_score'],
                    'score': item.get('score', 95),
                    'score_breakdown': item.get('score_breakdown', {}),
                    'persona_fit_reason': item.get('persona_fit_reason', ''),
                    'file': fp
                })
    except Exception as e:
        print(f"Error {fp}: {e}")

print(f"Found {len(candidates)} candidates in data/*.json:")
for i, c in enumerate(candidates):
    print(f"{i+1}. [{c['views']}] {c['code']} ({c['page']}) -> Sim={c['sim']}% | lines={c['lines_count']} | {c['title'][:40]}")
