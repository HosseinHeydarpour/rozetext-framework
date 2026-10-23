import json
import sys
import os
import re

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
current_codes = {r['shortcode'] for r in app36}

def parse_views(v_str):
    if not v_str:
        return 0
    v_str = str(v_str).strip().upper().replace(',', '')
    if 'M' in v_str:
        return float(v_str.replace('M', '')) * 1_000_000
    if 'K' in v_str:
        return float(v_str.replace('K', '')) * 1_000
    try:
        return float(v_str)
    except:
        return 0

harvest_dir = 'data'
candidates = []
for fname in os.listdir(harvest_dir):
    if fname.startswith('harvest_') and fname.endswith('.json'):
        fpath = os.path.join(harvest_dir, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                items = json.load(f)
                if isinstance(items, list):
                    for it in items:
                        href = it.get('href', '')
                        m = re.search(r'/reel/([A-Za-z0-9_-]+)/', href)
                        sc = m.group(1) if m else None
                        views_raw = it.get('text', '')
                        views_val = parse_views(views_raw)
                        author = '@' + fname.replace('harvest_', '').replace('.json', '')
                        if sc and sc not in db_codes and sc not in current_codes and views_val >= 500_000:
                            candidates.append({
                                'shortcode': sc,
                                'views': views_raw,
                                'views_num': views_val,
                                'author': author,
                                'url': f'https://www.instagram.com/reel/{sc}/'
                            })
        except Exception as e:
            pass

# Also check other files in data
for extra_file in ['data/scraped_vahid_yeharf.json', 'data/scraped_target_high_views.json', 'data/golden_inspected_pool.json', 'data/all_harvested_ranked.json']:
    if os.path.exists(extra_file):
        try:
            with open(extra_file, 'r', encoding='utf-8') as f:
                items = json.load(f)
                if isinstance(items, list):
                    for it in items:
                        sc = it.get('shortcode') or it.get('id') or it.get('code')
                        if not sc and it.get('url'):
                            m = re.search(r'/reel/([A-Za-z0-9_-]+)/', it.get('url'))
                            if m:
                                sc = m.group(1)
                        views_raw = it.get('views') or it.get('play_count') or ''
                        views_val = parse_views(views_raw)
                        author = it.get('author') or it.get('owner_username') or 'unknown'
                        if sc and sc not in db_codes and sc not in current_codes and views_val >= 500_000:
                            candidates.append({
                                'shortcode': sc,
                                'views': str(views_raw),
                                'views_num': views_val,
                                'author': author,
                                'url': f'https://www.instagram.com/reel/{sc}/'
                            })
        except:
            pass

# Deduplicate candidates by shortcode
unique_cands = {}
for c in candidates:
    if c['shortcode'] not in unique_cands:
        unique_cands[c['shortcode']] = c

candidates = sorted(unique_cands.values(), key=lambda x: x['views_num'], reverse=True)
print(f"Total unique candidates with >=500K views: {len(candidates)}")
for c in candidates[:25]:
    print(f"{c['shortcode']:<12} | {c['author']:<22} | {c['views']:<8} | {c['url']}")
