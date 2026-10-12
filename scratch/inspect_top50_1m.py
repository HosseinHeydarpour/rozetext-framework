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
qualified_1m = []

for i, b in enumerate(blocks[1:], 1):
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
    
    # 1M check
    is_1m = ('میلیون' in views_str or 'M' in views_str) and not any(k in views_str for k in ['۰٫', '0.'])
    if not is_1m:
        continue
        
    in_db = link in db_urls or any(code in u for u in db_urls if code)
    res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
    
    # DB dup check
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
            
    # lines check 7..16
    lines_ok = 7 <= len(lines) <= 16
    
    print(f"Block #{i} [{code}] | Views: {views_str} | Lines: {len(lines)} (OK: {lines_ok})")
    print(f"  In DB: {in_db} | DB Dup: {db_dup} | Hist Dup: {res_hist['is_duplicate']} (sim={res_hist['similarity_score']:.1f}%) | Closest: {res_hist.get('duplicate_of_reel')}")
    print(f"  First line: {lines[0] if lines else ''}")
    print("-" * 50)
    
    if not in_db and not db_dup and not res_hist['is_duplicate'] and lines_ok:
        qualified_1m.append({
            'code': code,
            'link': link,
            'page': page,
            'views_str': views_str,
            'lines': len(lines),
            'txt': txt
        })

print(f"\n================ TOTAL QUALIFIED 1M+ FROM TOP 50: {len(qualified_1m)} ================")
for q in qualified_1m:
    print(f"\nCode: {q['code']} | Views: {q['views_str']} | Lines: {q['lines']} | Page: {q['page']}")
    print(q['txt'])
