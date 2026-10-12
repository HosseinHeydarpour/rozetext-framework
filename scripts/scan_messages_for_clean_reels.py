import json, glob, sys, os, re
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

dir_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\messages'
all_files = glob.glob(os.path.join(dir_path, '*.json'))

print(f"Scanning {len(all_files)} messages...")

candidates = []

for f in all_files:
    try:
        with open(f, 'r', encoding='utf-8') as jf:
            d = json.load(jf)
    except Exception:
        continue
    content = d.get('content', '')
    if not content or len(content) < 50:
        continue
        
    # Search for blocks like "### ... ریلز `CODE`" or "https://www.instagram.com/reel/CODE"
    reels_found = re.finditer(r'(?:https://www\.instagram\.com/reel/|/reel/|ریلز\s*`?)([A-Za-z0-9_-]{10,12})`?', content)
    for m in reels_found:
        sc = m.group(1)
        if sc in db_codes or sc in already_selected:
            continue
            
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + 1500)
        chunk = content[start:end]
        
        # Check views 1M+
        v_match = re.search(r'(?:[1-9]\d*[\.,]\d*M|[1-9]\d*M|[۱-۹]\d*[\.,\u066b][۰-۹]*\s*میلیون|[۱-۹]\d*\s*میلیون|\b[1-9]\d{6,}\b)', chunk)
        if not v_match:
            continue
            
        # Check for code blocks ```text ... ``` or text lines
        txt_m = re.search(r'```(?:text)?\n(.*?)```', chunk, re.DOTALL)
        if txt_m:
            txt = txt_m.group(1).strip()
        else:
            # Look for lines
            lines_m = [l.strip() for l in chunk.splitlines() if len(l.strip()) > 10 and not any(k in l for k in ['http', 'ویو', 'لایک', '#', 'بازدید', 'آمار', '===', '---'])]
            txt = '\n'.join(lines_m[:16])
            
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if len(lines) < 7 or len(lines) > 16:
            continue
            
        # Blacklist
        bad_words = ['مولانا', 'شمس', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
        if any(bw in txt for bw in bad_words):
            continue
            
        # Deduplication
        hist = ENGINE.check_duplicate_against_history(txt, txt)
        if hist['is_duplicate']:
            continue
            
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
            
        candidates.append({
            'code': sc,
            'views': v_match.group(0),
            'lines': len(lines),
            'text': txt,
            'hist_sim': hist['similarity_score'],
            'db_sim': max_dbsim,
            'msg_file': os.path.basename(f)
        })

# Unique by code
seen = set()
unique_cands = []
for c in candidates:
    if c['code'] not in seen:
        seen.add(c['code'])
        unique_cands.append(c)

print(f"\n=== FOUND {len(unique_cands)} CLEAN 1M+ CANDIDATES IN MESSAGES ===")
for c in unique_cands:
    print(f"[{c['code']}] Views: {c['views']} | Lines: {c['lines']} | Hist: {c['hist_sim']:.1f}% | DB: {c['db_sim']:.1%}")
    print(c['text'])
    print('-'*50)
