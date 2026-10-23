import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

with open('data/verified_36_reels_clean.json', 'r', encoding='utf-8') as f:
    app36 = json.load(f)
app_codes = {r['shortcode'] for r in app36}

for target_file in ['data/hunted-42-fresh-multiaccount-verified.json', 'data/hunted-42-reels-batch-verified.json', 'data/expansion_30_to_120_verified.json', 'data/clean_harvested_corpus.json']:
    if not os.path.exists(target_file):
        continue
    with open(target_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    print(f"=== {target_file} ({len(items)} items) ===")
    for it in items:
        sc = it.get('shortcode') or it.get('id')
        v = it.get('views') or it.get('source_views') or ''
        txt = it.get('text') or it.get('content') or it.get('extracted_raw_text') or ''
        lines = [l.strip() for l in txt.split('\n') if l.strip()]
        if sc and sc not in db_codes and sc not in app_codes and 7 <= len(lines) <= 16:
            res = engine.check(txt)
            if not res['is_duplicate'] and res['similarity_score'] < 35:
                print(f"PASS: {sc:<14} | views: {str(v):<10} | lines: {len(lines)} | sim: {res['similarity_score']:.1f}% | {it.get('author') or it.get('source_page')}")
                print(txt[:100] + '...')
                print('-'*50)
