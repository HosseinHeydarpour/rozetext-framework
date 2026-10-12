import json
import re
import sys
import os
import glob
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

sys.stdout.reconfigure(encoding='utf-8')
engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
existing_scheduled_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

print("=== Checking all JSON files in data/ ===")
for path in glob.glob('data/*.json'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        continue
    items = []
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and 'scripts' in data:
        items = data['scripts']
    elif isinstance(data, dict) and 'reels' in data:
        items = data['reels']
    
    print(f"\nFile: {path} ({len(items)} items)")
    cands = 0
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
        if not url:
            continue
        content = item.get('content', '') or item.get('extracted_raw_text', '')
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        
        if views_num >= 1000000:
            dup_res = engine.check_duplicate_against_history(content, content)
            in_db = url in existing_scheduled_urls
            print(f"  - [{views_str}] {item.get('source_page')} | Lines: {len(lines)} | InDB: {in_db} | Dup: {dup_res['is_duplicate']} ({dup_res['similarity_score']:.1f}%) | {url}")
            if not dup_res['is_duplicate'] and not in_db and len(lines) >= 7 and len(lines) <= 16:
                cands += 1
    print(f"  => Usable 1M+ candidates in this file: {cands}")
