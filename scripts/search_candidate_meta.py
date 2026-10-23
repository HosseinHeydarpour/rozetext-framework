import os
import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

with open('data/verified_36_reels_clean.json', 'r', encoding='utf-8') as f:
    app36 = json.load(f)
app_codes = {r['shortcode'] for r in app36}

frames = os.listdir('downloads/frames')

targets = {}
for fname in ['data/harvest_shadighorbanyy.json', 'data/harvest_vahidrezakhoshbayan.json', 'data/harvest_horaetemad.json', 'data/harvest_zahraa_deep.json']:
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            items = json.load(f)
            for it in items:
                href = it.get('href', '')
                m = re.search(r'/reel/([A-Za-z0-9_-]+)/', href)
                if m:
                    sc = m.group(1)
                    targets[sc] = {'views': it.get('text', ''), 'file': fname}

print(f"Total target reels in harvest: {len(targets)}")
for sc, meta in targets.items():
    if sc not in db_codes and sc not in app_codes:
        matching = [f for f in frames if sc in f]
        if matching:
            v_str = meta['views']
            print(f"{sc:<14} | views: {v_str:<8} | {meta['file']:<35} | {matching}")
