import json, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

already_selected = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DZSr1vMN1mr', 'DPjI0mTCIPs', 
    'DKm6Qn6I9vQ', 'DPRj9ddCF5T', 'DbyY0F7tmAn', 'Dd9GQ7HsdZM', 'DdEeNFfs5V3'
}

p = r'C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json'
with open(p, 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Checking {len(items)} items from batch2_wave1_29...")
clean_matches = []

for i, it in enumerate(items):
    sc = it.get('shortcode')
    views = it.get('views')
    txt = it.get('video_text', '')
    txt = txt.strip('«»" \t\n')
    # strip author signature if present
    txt = re.sub(r'—\s*وحیدرضا خوش‌بیان.*$', '', txt).strip()
    
    in_db = (sc in db_codes) or (sc in already_selected)
    
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    
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
            
    is_clean = (not in_db) and (not hist['is_duplicate']) and (not dup_db)
    
    if is_clean:
        clean_matches.append((sc, views, txt, hist['similarity_score'], max_dbsim, it))
        print(f"[{i}] {sc} ({views}) | CLEAN PASS | Hist: {hist['similarity_score']:.1f}% | DB: {max_dbsim:.1%}")
        print(f"    Text: {txt[:70]}...")
    else:
        status = "IN_DB" if in_db else f"HistDup:{hist['is_duplicate']}({hist['similarity_score']:.1f}%) DBDup:{dup_db}({max_dbsim:.1%})"
        print(f"[{i}] {sc} ({views}) | FAIL: {status}")

print(f"\nTotal Clean Matches Found: {len(clean_matches)}")
