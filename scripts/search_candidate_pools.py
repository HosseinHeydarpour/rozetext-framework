import json
import glob
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()

target_files = [
    'data/hunted-42-fresh-multiaccount-verified.json',
    'data/hunted-42-reels-batch-verified.json',
    'data/expansion_candidates_verified.json',
    'data/golden_inspected_pool.json',
    'data/clean_pool_discovered.json',
    'data/scraped_vahid_yeharf.json',
    'data/scraped_target_high_views.json'
]

# Load existing DB to make sure we don't pick anything already in DB
with open('data/scripts-db.json', encoding='utf-8') as f:
    db = json.load(f)
existing_urls = {s.get('source_url') for s in db['scripts'] if s.get('source_url')}
existing_titles = {s.get('title') for s in db['scripts'] if s.get('title')}

# Load our 29 approved reels
with open('data/approved_24_reels.json', encoding='utf-8') as f:
    app24 = json.load(f)
app_ids = {a['id'] for a in app24}
# plus the 5 added from shadi & horae
app_ids.update({'DdeYIgZqlG9', 'DdhIZDEK8_S', 'DdotWXnCiBy', 'DdzFv9hCAZO', 'DeHxCX3i3xc', 'Ded4vxjsQX3'})

candidates_found = []

for tf in target_files:
    if not os.path.exists(tf):
        continue
    with open(tf, encoding='utf-8') as f:
        try:
            data = json.load(f)
        except:
            continue
    items = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
    for it in items:
        if not isinstance(it, dict):
            continue
        code = it.get('id') or it.get('shortcode') or it.get('code')
        if not code or code in app_ids:
            continue
        url = it.get('url') or it.get('source_url') or f"https://www.instagram.com/reel/{code}/"
        if url in existing_urls:
            continue
        text = it.get('text') or it.get('content') or it.get('extracted_raw_text') or ''
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        if not (7 <= len(lines) <= 20):
            continue
        views = it.get('views') or it.get('source_views') or it.get('views_str') or '0'
        # filter out halekhoub
        author = it.get('author') or it.get('source_page') or ''
        if 'halekhoub' in str(author) or 'halekhoub' in str(url):
            continue
        # filter out Molana / Shams / poets
        if any(w in text for w in ['مولانا', 'شمس تبریزی', 'حافظ', 'سعدی', 'خیام', 'فروغ فرخزاد', 'سهراب سپهری', 'فاضل نظری']):
            continue
        
        candidates_found.append({
            'code': code,
            'url': url,
            'author': author,
            'views': views,
            'text': '\n'.join(lines),
            'lines_count': len(lines),
            'source_file': tf
        })

print(f"Total potential candidates found: {len(candidates_found)}")

# Deduplicate candidates_found by code
unique_cands = {}
for c in candidates_found:
    if c['code'] not in unique_cands:
        unique_cands[c['code']] = c

print(f"Unique potential candidates: {len(unique_cands)}")

passed = []
for code, c in unique_cands.items():
    res = engine.check(c['text'])
    score = res['similarity_score']
    is_dup = res['is_duplicate']
    if not is_dup:
        print(f"PASS: {code:<15} | Score: {score:4.1f}% | Lines: {c['lines_count']:2d} | Views: {str(c['views']):<10} | {c['author']}")
        c['similarity_score'] = score
        passed.append(c)

print(f"\nTotal Clean Passed: {len(passed)}")
with open('downloads/fresh_pool_passed.json', 'w', encoding='utf-8') as f:
    json.dump(passed, f, ensure_ascii=False, indent=2)
