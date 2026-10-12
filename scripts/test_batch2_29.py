import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_db_texts = []
for s in db.get('scripts', []):
    t = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if t.strip():
        existing_db_texts.append(t.strip())

p = r"C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json"
with open(p, 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Checking {len(items)} items...")
for it in items:
    sc = it.get('shortcode')
    v = it.get('views', '')
    txt = it.get('video_text', '')
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    is_1m = ('1M' in v or '2M' in v or '3M' in v or '4M' in v or '5M' in v or '1.5M' in v or '1.2M' in v or '1.1M' in v or '1.3M' in v or '1.9M' in v or '2.1M' in v or '2.5M' in v or '3.7M' in v or '3.9M' in v)
    if not is_1m:
        continue
    res_hist = ENGINE.check_duplicate_against_history(txt, txt)
    
    # check db
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    db_dup = False
    for dbt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(dbt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(dbt, 4)
        common_ngrams = c_ngrams & s_ngrams
        if len(common_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            break
    print(f"{sc} | {v} | lines={len(lines)} | hist_dup={res_hist['is_duplicate']} ({res_hist['similarity_score']}%) | db_dup={db_dup}")
