import json
import re
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

sys.stdout.reconfigure(encoding='utf-8')
engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
existing_scheduled_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f'Total items in verified batch: {len(items)}')

candidates = []
for item in items:
    views_str = str(item.get('source_views', '0'))
    m = re.search(r'([\d\.]+)\s*(M|K|k|m)?', views_str)
    views_num = 0
    if m:
        val = float(m.group(1))
        unit = (m.group(2) or '').upper()
        if unit == 'M':
            views_num = int(val * 1000000)
        elif unit == 'K':
            views_num = int(val * 1000)
        else:
            views_num = int(val)
    
    url = item.get('source_url', '').strip()
    content = item.get('content', '') or item.get('extracted_raw_text', '')
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    
    dup_res = engine.check_duplicate_against_history(content, content)
    in_db = url in existing_scheduled_urls
    is_halekhoub = 'halekhoub' in item.get('source_page', '').lower() or 'halekhoub' in url.lower()
    
    if views_num >= 1000000 and not is_halekhoub and not in_db and not dup_res['is_duplicate'] and len(lines) >= 7 and len(lines) <= 16:
        candidates.append({
            'url': url,
            'source_page': item.get('source_page'),
            'views': views_num,
            'views_str': views_str,
            'lines_count': len(lines),
            'sim': dup_res['similarity_score'],
            'title': item.get('title'),
            'hook': item.get('hook'),
            'content': content,
            'item': item
        })

print(f'Matching candidates with >=1M views, 7-16 lines, no halekhoub, not in db, not dup: {len(candidates)}')
for c in candidates:
    print(f"- {c['views_str']} ({c['source_page']}) [sim: {c['sim']:.1f}%, lines: {c['lines_count']}]: {c['url']}")
    print(f"  Hook: {c['hook']}")
