import os, sys, glob, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []) if s.get('source_url'))
db_codes = set()
for u in db_urls:
    m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
    if m: db_codes.add(m.group(1))

existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), txt.strip()))

# Verified 5 so far:
verified_5 = {'DNTYt15oqYj', 'DZDRxCkNgjw', 'DbyY0F7tmAn', 'DPRj9ddCF5T', 'DKm6Qn6I9vQ'}

files_to_scan = [
    r'D:\rozetext content\top_15_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt',
    r'D:\rozetext content\delneveshte_top_posts.txt'
]

clean_candidates = []

for fp in files_to_scan:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    print(f"\n================ Scanning {os.path.basename(fp)} ================")
    # Look for entries with links, views, text
    # Let's split by number or bullet
    blocks = re.split(r'\n(?=[۰-۹0-9]+[\.\-]\s+)', content)
    print(f"Blocks found: {len(blocks)}")
    
    for b in blocks:
        m_link = re.search(r'https?://[^\s\n]+/reel/([A-Za-z0-9_-]+)/?', b)
        if not m_link:
            m_link = re.search(r'https?://[^\s\n]+/(?:p|reels)/([A-Za-z0-9_-]+)/?', b)
        if not m_link:
            continue
            
        code = m_link.group(1)
        full_url = m_link.group(0)
        
        # Check views
        m_views = re.search(r'(?:آمار|ویو|بازدید|views)[^\n:]*[:\s]+([^\n]+)', b, re.IGNORECASE)
        views_str = m_views.group(1).strip() if m_views else ''
        
        # Check text
        m_text = re.search(r'[«"]([^»"]+)[»"]', b)
        if not m_text:
            m_text = re.search(r'```text\n(.*?)```', b, re.DOTALL)
        if not m_text:
            m_text = re.search(r'(?:متن|متن روی ویدیو|متن داخل تصویر)[^\n:]*[:\s]*\n+(.*?)(?=\n\n|\n[۰-۹0-9]+|\Z)', b, re.DOTALL)
            
        if not m_text:
            continue
            
        txt = m_text.group(1).strip()
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        line_count = len(lines)
        
        # Views 1M+ check
        is_1m = ('میلیون' in views_str or 'M' in views_str or '1,' in views_str or '2,' in views_str or '3,' in views_str or '4,' in views_str or '5,' in views_str or '6,' in views_str or '7,' in views_str or '8,' in views_str or '9,' in views_str or '10,' in views_str) and not any(k in views_str for k in ['0.', '۰٫'])
        
        in_db = code in db_codes or full_url in db_urls
        in_v5 = code in verified_5
        
        res_hist = ENGINE.check_duplicate_against_history(lines[0] if lines else '', txt)
        
        c_tokens = ENGINE._normalize_persian_tokens(txt)
        c_ngrams = ENGINE._extract_ngrams(txt, 4)
        db_dup = False
        closest_db = None
        for s_id, s_title, s_txt in existing_db_texts:
            s_tokens = ENGINE._normalize_persian_tokens(s_txt)
            overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
            s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
            common_ngrams = c_ngrams & s_ngrams
            if len(common_ngrams) >= 2 or overlap >= 0.40:
                db_dup = True
                closest_db = f"{s_id}: {s_title}"
                break
                
        bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
        has_bad = any(bw in txt for bw in bad_words) or 'halekhoub' in b
        
        if is_1m and 7 <= line_count <= 16 and not in_db and not in_v5 and not db_dup and not res_hist['is_duplicate'] and not has_bad:
            print(f"  >>> QUALIFIED 1M+ [{code}] Views: {views_str} | Lines: {line_count}")
            print(f"      Hook: {lines[0]}")
            print(f"      Text:\n{txt}\n" + "-"*40)
            clean_candidates.append({
                'code': code,
                'url': full_url,
                'views': views_str,
                'lines': line_count,
                'text': txt,
                'file': os.path.basename(fp)
            })

print(f"\nTOTAL NEW CLEAN 1M+ REELS FOUND: {len(clean_candidates)}")
