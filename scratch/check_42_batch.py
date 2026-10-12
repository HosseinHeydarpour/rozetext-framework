import os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import ENGINE

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch42 = json.load(f)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Collect DB urls and shortcodes
db_scripts = db.get('scripts', [])
db_urls = set(s.get('source_url', '').strip() for s in db_scripts if s.get('source_url'))
db_shortcodes = set()
for u in db_urls:
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    if m: db_shortcodes.add(m.group(1))

# Collect DB texts
existing_db_texts = []
for s in db_scripts:
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), s.get('scheduled_date'), s.get('scheduled_slot'), txt.strip()))

print(f"Total reels in hunted-42: {len(batch42)}")
print(f"Total scripts in scripts-db: {len(db_scripts)}")

clean_candidates = []

for idx, r in enumerate(batch42, 1):
    url = r.get('source_url', '').strip()
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
    sc = m.group(1) if m else f"item_{idx}"
    
    views = str(r.get('source_views', ''))
    txt = r.get('extracted_raw_text') or r.get('content') or ''
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    line_count = len(lines)
    
    # 1M check
    is_1m = ('M' in views or 'میلیون' in views or any(k in views for k in ['1,', '2,', '3,', '4,', '5,', '6,', '7,', '8,', '9,', '10,'])) and not any(k in views for k in ['0.', '۰٫'])
    
    # In DB check
    in_db = url in db_urls or sc in db_shortcodes
    
    # Check duplicate against published history
    res_hist = ENGINE.check_duplicate_against_history(lines[0] if lines else '', txt)
    
    # Check duplicate against DB
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    db_dup = False
    closest_db = None
    for s_id, s_title, s_date, s_slot, s_txt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(s_txt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
        common_ngrams = c_ngrams & s_ngrams
        if len(common_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            closest_db = f"{s_id} ({s_date} slot {s_slot}): {s_title}"
            break
            
    # Persona
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    bad_persona = any(bw in txt for bw in bad_words) or '@halekhoub' in r.get('source_page', '')
    
    status_str = f"#{idx:02d} [{sc}] {views} | {line_count}L"
    if in_db: status_str += " | InDB"
    if db_dup: status_str += f" | DBDup({closest_db})"
    if res_hist['is_duplicate']: status_str += f" | HistDup(sim={res_hist['similarity_score']:.1f}% #{res_hist.get('duplicate_of_reel')})"
    if bad_persona: status_str += " | BadPersona"
    if not is_1m: status_str += " | <1M"
    if line_count < 7 or line_count > 16: status_str += f" | LinesOutOfRange({line_count})"
    
    is_clean = is_1m and (7 <= line_count <= 16) and not in_db and not db_dup and not res_hist['is_duplicate'] and not bad_persona
    if is_clean:
        status_str += " >>> PASS CLEAN!"
        clean_candidates.append(r)
        
    print(status_str)

print(f"\n================ TOTAL CLEAN CANDIDATES FROM 42 BATCH: {len(clean_candidates)} ================")
for c in clean_candidates:
    u = c.get('source_url', '')
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    sc = m.group(1) if m else 'N/A'
    first_line = (c.get('extracted_raw_text') or '').splitlines()[0]
    print(f"[{sc}] {c.get('source_views')} | Lines: {len((c.get('extracted_raw_text') or '').splitlines())} | Hook: {first_line}")
