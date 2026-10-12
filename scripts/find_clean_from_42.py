import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

print(f"Checking {len(batch)} reels from 42-batch against 81 DB scripts & history...")
clean_available = []

for i, it in enumerate(batch):
    txt = it.get('extracted_raw_text') or it.get('content') or ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    u = it.get('source_url', '').rstrip('/')
    sc = u.split('/reel/')[-1].split('/')[0] if '/reel/' in u else ''
    views = it.get('source_views', '')
    page = it.get('source_page', '')
    
    if sc in db_codes:
        continue
        
    # Check lines 7..16
    if len(lines) < 7 or len(lines) > 16:
        continue
        
    # Blacklist words
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز', 'عید من روزیه']
    if any(bw in txt for bw in bad_words):
        continue
        
    # Hist duplicate
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    if hist['is_duplicate']:
        continue
        
    # DB duplicate check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    max_dbsim = 0
    dup_db = False
    for dbt in db_texts:
        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
        sim = len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens)))
        if sim > max_dbsim:
            max_dbsim = sim
        dbt_ngrams = ENGINE._extract_ngrams(dbt, 4)
        if len(c_ngrams & dbt_ngrams) >= 2 or sim >= 0.40:
            dup_db = True
            break
            
    if dup_db:
        continue
        
    clean_available.append({
        'idx': i+1,
        'sc': sc,
        'page': page,
        'views': views,
        'lines': len(lines),
        'hook': lines[0] if lines else '',
        'hist_sim': hist['similarity_score'],
        'db_sim': max_dbsim,
        'text': txt,
        'full_item': it
    })

print(f"Found {len(clean_available)} clean available reels!")
for c in clean_available:
    print(f"#{c['idx']} [{c['sc']}] ({c['views']} - {c['page']}) | Lines: {c['lines']} | Hist: {c['hist_sim']:.1f}% | DB: {c['db_sim']:.1%}")
    print(f"  Hook: {c['hook']}")

with open('scratch/clean_from_42.json', 'w', encoding='utf-8') as f:
    json.dump([c['full_item'] for c in clean_available], f, ensure_ascii=False, indent=2)
print("Saved to scratch/clean_from_42.json")
