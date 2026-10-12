import os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import ENGINE

# 8 already cleared shortcodes
cleared_8 = {'DNTYt15oqYj', 'DZDRxCkNgjw', 'DbyY0F7tmAn', 'DPRj9ddCF5T', 'DKm6Qn6I9vQ', 'C5WPI8OCK4x', 'DaYpUkIIdSr', 'DIGSOwBNUgp'}

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), s.get('scheduled_date'), s.get('scheduled_slot'), txt.strip()))

with open(r'D:\rozetext-framework\scratch\subagent_12_reels_full.txt', 'r', encoding='utf-8') as f:
    raw_sub = f.read()

items = re.split(r'###\s*\d+\.\s*', raw_sub)
candidates = []
for it in items[1:]:
    m_url = re.search(r'source_url[^\n:]*:\s*(https?://[^\s\n\*\)]+)', it)
    m_views = re.search(r'source_views[^\n:]*:\s*([^\n\*\)]+)', it)
    m_page = re.search(r'source_page[^\n:]*:\s*([^\n\*\)]+)', it)
    m_text = re.search(r'```(?:text)?\s*\n(.*?)\n```', it, re.DOTALL)
    url = m_url.group(1).strip() if m_url else ''
    views = m_views.group(1).strip() if m_views else ''
    page = m_page.group(1).strip() if m_page else ''
    txt = m_text.group(1).strip() if m_text else ''
    m_code = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', url)
    code = m_code.group(1) if m_code else ''
    candidates.append({'code': code, 'url': url, 'page': page, 'views': views, 'text': txt})

print(f'Parsed {len(candidates)} candidates from subagent file.\n')

passed = []
for c in candidates:
    code = c['code']
    text = c['text']
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    l_count = len(lines)
    
    # 1. Check history
    res_hist = ENGINE.check_duplicate_against_history(text, text)
    
    # 2. Check DB
    c_tokens = ENGINE._normalize_persian_tokens(text)
    c_ngrams = ENGINE._extract_ngrams(text, 4)
    db_dup = False
    closest_db = None
    for s_id, s_title, s_date, s_slot, s_txt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(s_txt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
        if len(c_ngrams & s_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            closest_db = f"{s_id} ({s_date} slot {s_slot}): {s_title} (overlap={overlap*100:.1f}%)"
            break
            
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    bad_persona = any(bw in text for bw in bad_words) or '@halekhoub' in c['page']
    
    is_valid = (7 <= l_count <= 16) and not res_hist['is_duplicate'] and not db_dup and not bad_persona and (code not in cleared_8)
    
    status = 'PASS' if is_valid else 'FAIL'
    v_str = c['views']
    print(f"[{status}] Code: {code} | Views: {v_str} | Lines: {l_count}")
    if res_hist['is_duplicate']:
        print(f"   -> Hist Dup: Reel #{res_hist.get('duplicate_of_reel')} ({res_hist['similarity_score']:.1f}%)")
    if db_dup:
        print(f"   -> DB Dup: {closest_db}")
    if bad_persona:
        print(f"   -> Bad Persona")
    if code in cleared_8:
        print(f"   -> Already in cleared 8")
    if not (7 <= l_count <= 16):
        print(f"   -> Line count out of range: {l_count}")
        
    if is_valid:
        passed.append(c)

print(f'\nTOTAL PASSED: {len(passed)}')
for p in passed:
    print(f" - [{p['code']}] {p['page']} ({p['views']})")
