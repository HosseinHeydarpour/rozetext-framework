import os, glob, json, re, sys
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

# Find all files with batch in name
files = glob.glob(r'C:\Users\User\.gemini\antigravity\brain\**\*batch*', recursive=True)
files += glob.glob(r'C:\Users\User\.gemini\antigravity\brain\**\*review*', recursive=True)
files = list(set(files))

print(f"Checking {len(files)} review/batch files...")

candidates = []

for fp in files:
    if not (fp.endswith('.json') or fp.endswith('.md')):
        continue
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        continue
        
    if fp.endswith('.json'):
        try:
            data = json.loads(content)
            items = data if isinstance(data, list) else data.get('scripts', data.get('reels', []))
            for it in items:
                u = it.get('source_url') or it.get('url') or ''
                sc = u.rstrip('/').split('/')[-1] if u else ''
                txt = it.get('extracted_raw_text') or it.get('content') or it.get('text') or ''
                views = str(it.get('source_views') or it.get('views') or '')
                page = it.get('source_page') or it.get('page') or ''
                candidates.append((sc, u, page, views, txt, fp))
        except Exception:
            pass
    elif fp.endswith('.md'):
        # Parse blocks in markdown
        blocks = re.split(r'###\s+', content)
        for b in blocks:
            url_m = re.search(r'https://www\.instagram\.com/reel/([A-Za-z0-9_-]+)', b)
            if not url_m:
                continue
            sc = url_m.group(1)
            u = url_m.group(0)
            views_m = re.search(r'(?:views|بازدید|آمار|ویو)[^\n]*', b, re.IGNORECASE)
            views = views_m.group(0) if views_m else ''
            page_m = re.search(r'@([A-Za-z0-9_.-]+)', b)
            page = '@' + page_m.group(1) if page_m else ''
            
            # Find text block
            txt_m = re.search(r'```(?:text)?\n(.*?)```', b, re.DOTALL)
            txt = txt_m.group(1).strip() if txt_m else ''
            if not txt:
                # Look for lines
                lines_m = re.findall(r'^[^\n#|*`-].*$', b, re.MULTILINE)
                txt = '\n'.join([l.strip() for l in lines_m if len(l.strip()) > 5])
            candidates.append((sc, u, page, views, txt, fp))

print(f"Total candidate entries parsed: {len(candidates)}")

tested = set()
clean_found = []

for sc, u, page, views, txt, fp in candidates:
    if not sc or sc in tested or sc in already_selected or sc in db_codes:
        continue
    tested.add(sc)
    
    # Check 1M+ views
    # e.g., '1M', '1.2M', 'میلیون', or numbers >= 1,000,000
    is_1m = bool(re.search(r'(?:[1-9]\d*[\.,]\d*M|[1-9]\d*M|[۱-۹]\d*[\.,\u066b][۰-۹]*\s*میلیون|[۱-۹]\d*\s*میلیون|\b[1-9]\d{6,}\b)', views))
    if not is_1m:
        continue
        
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if len(lines) < 7 or len(lines) > 16:
        continue
        
    # Blacklist
    if '@halekhoub' in page or 'halekhoub' in page:
        continue
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    if any(bw in txt for bw in bad_words):
        continue
        
    # Hist duplicate
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    if hist['is_duplicate']:
        continue
        
    # DB duplicate check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    if len(c_tokens) < 4:
        continue
        
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
        
    clean_found.append({
        'sc': sc,
        'u': u,
        'page': page,
        'views': views,
        'lines': len(lines),
        'hook': lines[0] if lines else '',
        'hist_sim': hist['similarity_score'],
        'db_sim': max_dbsim,
        'text': txt,
        'file': fp
    })

print(f"\n=== CLEAN 1M+ CANDIDATES FOUND: {len(clean_found)} ===")
for c in clean_found:
    print(f"[{c['sc']}] ({c['views']} - {c['page']}) | Lines: {c['lines']} | Hist: {c['hist_sim']:.1f}% | DB: {c['db_sim']:.1%}")
    print(f"  Hook: {c['hook']}")
    print(f"  Source file: {os.path.basename(c['file'])}")
