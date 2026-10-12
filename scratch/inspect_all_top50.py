import os, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8', errors='ignore') as f:
    raw_content = f.read()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))
existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append(txt.strip())

blocks = re.split(r'\n(?=[۰-۹0-9]+\.\s+پیج)', raw_content)
print(f"Total blocks: {len(blocks)}")

for i, b in enumerate(blocks):
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
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    
    m_code = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', link)
    code = m_code.group(1) if m_code else ''
    
    # Check 1M
    is_1m = 'M' in views_str or 'میلیون' in views_str or any(k in views_str for k in ['1,', '2,', '3,', '4,', '5,', '6,', '7,', '8,', '9,', '10,'])
    
    res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
    
    # db dup
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
            
    in_db = link in db_urls or any(code in u for u in db_urls if code)
    
    print(f"#{i} [{code}] Views: {views_str} | Lines: {len(lines)} | InDB: {in_db} | DBDup: {db_dup} | HistDup: {res_hist['is_duplicate']} (sim={res_hist['similarity_score']}%)")
    if not in_db and not db_dup and not res_hist['is_duplicate'] and 7 <= len(lines) <= 16:
        print(f"   >>> QUALIFIED! Page: {page} | Hook: {lines[0]}")
