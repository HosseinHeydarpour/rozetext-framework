import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
from server import ENGINE

base = r'C:\Users\User\.gemini\antigravity\brain'
files = []
for root, dirs, fnames in os.walk(base):
    for f in fnames:
        if f.endswith('.json') or f.endswith('.jsonl'):
            files.append(os.path.join(root, f))

found_candidates = {}

for fp in files:
    if 'scripts-db' in fp:
        continue
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        continue

    # Look for candidate scripts in json array form
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('source_url'):
                    su = item['source_url']
                    sc = su.rstrip('/').split('/')[-1]
                    if sc not in found_candidates:
                        found_candidates[sc] = item
        elif isinstance(data, dict):
            for k in ['scripts', 'items', 'reels']:
                if k in data and isinstance(data[k], list):
                    for item in data[k]:
                        if isinstance(item, dict) and item.get('source_url'):
                            su = item['source_url']
                            sc = su.rstrip('/').split('/')[-1]
                            if sc not in found_candidates:
                                found_candidates[sc] = item
    except Exception:
        # Not a single json, maybe jsonl or mixed text
        pass

print(f'Total candidates found across files: {len(found_candidates)}')
over_1m = []
for sc, item in found_candidates.items():
    views_str = str(item.get('source_views', ''))
    txt = item.get('extracted_raw_text') or item.get('content') or ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    dup = ENGINE.check_duplicate_against_history(txt, txt)
    if ('M' in views_str or 'میلیون' in views_str or '10,' in views_str) and not dup['is_duplicate'] and len(lines) >= 7:
        over_1m.append((sc, views_str, len(lines), lines[0][:40], item))

print(f'Over 1M non-duplicate with >= 7 lines: {len(over_1m)}')
for sc, v, l, h, _ in over_1m:
    print(f' - {sc} | {v} | {l} lines | Hook: {h}')
