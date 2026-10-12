import os, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

def fa_to_en(text):
    fa_digits = '۰۱۲۳۴۵۶۷۸۹'
    en_digits = '0123456789'
    trans = str.maketrans(fa_digits, en_digits)
    return text.translate(trans)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

used_codes = set()
existing_db_texts = []
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append(txt.strip())

verified_9_codes = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DNTYt15oqYj', 'DZSr1vMN1mr',
    'DPjI0mTCIPs', 'DKm6Qn6I9vQ', 'DQHm9z6CMeL', 'DPRj9ddCF5T', 'DbyY0F7tmAn'
}

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8', errors='ignore') as f:
    raw_content = f.read()

# Split by numbered entries: e.g. "۱. پیج"
blocks = re.split(r'\n(?=[۰-۹0-9]+\.\s+پیج)', raw_content)

print(f"Total blocks found: {len(blocks)}")

candidates = []

for b in blocks:
    m_link = re.search(r'لینک:\s*(https?://[^\s\n]+)', b)
    m_views = re.search(r'آمار:\s*([^\n]+)', b)
    m_page = re.search(r'پیج\s*([^\n\s]+)', b)
    m_text = re.search(r'«([^»]+)»', b)
    
    if not (m_link and m_views and m_text):
        continue
        
    link = m_link.group(1).strip()
    views_str = m_views.group(1).strip()
    page = m_page.group(1).strip() if m_page else ''
    txt = m_text.group(1).strip()
    
    m_code = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', link)
    code = m_code.group(1) if m_code else ''
    
    # Parse views
    en_views_str = fa_to_en(views_str).replace('٬', '').replace(',', '')
    m_num = re.search(r'(\d+)', en_views_str)
    view_count = int(m_num.group(1)) if m_num else 0
    
    is_1m = view_count >= 1000000 or 'M' in views_str or 'میلیون' in views_str
    
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    line_count = len(lines)
    
    candidates.append({
        'code': code,
        'link': link,
        'page': page,
        'views_str': views_str,
        'view_count': view_count,
        'is_1m': is_1m,
        'line_count': line_count,
        'lines': lines,
        'txt': txt
    })

print(f"Parsed {len(candidates)} candidates.")

# Filter for our 3 remaining slots
clean_pool = []
for c in candidates:
    code = c['code']
    if not c['is_1m']:
        continue
    if code in used_codes:
        continue
    if code in verified_9_codes:
        continue
    if c['line_count'] < 7 or c['line_count'] > 16:
        continue
    if '@halekhoub' in c['page'] or 'halekhoub' in c['page']:
        continue
    txt = c['txt']
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    if any(bw in txt for bw in bad_words):
        continue
        
    res_hist = ENGINE.check_duplicate_against_history(c['lines'][0], txt)
    if res_hist['is_duplicate']:
        print(f"Skipping {code}: duplicate of Reel #{res_hist.get('duplicate_of_reel')} ({res_hist['similarity_score']}%)")
        continue
        
    # Check db dup
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    db_dup = False
    for s_txt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(s_txt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
        if len(c_ngrams & s_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            break
    if db_dup:
        print(f"Skipping {code}: duplicate of scripts-db")
        continue
        
    clean_pool.append(c)

print(f"\n================ CLEAN POOL (1M+, 7-16 lines, no dup): {len(clean_pool)} ================")
for c in clean_pool:
    print(f"\nCode: {c['code']} | Page: @{c['page']} | Views: {c['views_str']} | Lines: {c['line_count']}")
    print(f"Link: {c['link']}")
    print("Hook:", c['lines'][0])
    print("Full text:\n" + c['txt'])
