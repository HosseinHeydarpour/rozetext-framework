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
            db_codes.add(c.lower())

with open(r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for each item:
# \d+\.\s*پیج\s*([^\|]+)\|\s*لینک:\s*(https://[^\s\|]+)\s*\|\s*ویو:\s*([^\|]+)\|\s*نمره مستقل:\s*([^\n\r]+)
# متن دقیق داخل ویدیو:
# «([\s\S]*?)»

pattern = r'(\d+)\.\s*پیج\s*([^\|]+)\|\s*لینک:\s*(https://[^\s\|]+)\s*\|\s*ویو:\s*([^\|]+)\|\s*نمره مستقل:\s*([^\n\r]+)\s*\nمتن دقیق داخل ویدیو:\s*\n«?([\s\S]*?)»?(?=\n\s*\d+\.\s*پیج|\Z)'

matches = re.finditer(pattern, content)
items = []

for m in matches:
    num = m.group(1)
    page = m.group(2).strip()
    url = m.group(3).strip()
    views = m.group(4).strip()
    score = m.group(5).strip()
    raw_text = m.group(6).strip()
    raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
    
    code_match = re.search(r'reel[s]?/([A-Za-z0-9_-]+)', url)
    if not code_match:
        continue
    code = code_match.group(1)
    
    # check million
    is_million = False
    if 'M' in views or 'm' in views or 'میلیون' in views:
        is_million = True
    else:
        d = re.findall(r'[\d\.]+', views)
        if d and float(d[0]) >= 1000: # if e.g. 1000K
            is_million = True
            
    in_db = code.lower() in db_codes
    
    dup = engine.check_duplicate_against_history(raw_text, raw_text)
    
    items.append({
        'num': num,
        'page': page,
        'url': url,
        'code': code,
        'views': views,
        'is_million': is_million,
        'score': score,
        'in_db': in_db,
        'is_dup': dup['is_duplicate'],
        'sim': dup['similarity_score'],
        'text': raw_text
    })

print(f"Total matched items in batch 01: {len(items)}")
matching = [it for it in items if it['is_million'] and not it['in_db'] and not it['is_dup']]
print(f"Total FRESH 1M+ NON-DUPLICATES: {len(matching)}")

for it in matching:
    lines = [l for l in it['text'].split('\n') if l.strip()]
    print(f"#{it['num']} [{it['views']}] {it['code']} ({it['page']}) -> Sim={it['sim']}% | lines={len(lines)} | Hook: {it['text'][:40]}")
