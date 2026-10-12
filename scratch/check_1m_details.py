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

files_to_scan = [
    r'D:\rozetext content\top_15_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt'
]

for fp in files_to_scan:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    print(f"\n================ Scanning {os.path.basename(fp)} ================")
    blocks = re.split(r'\n(?=[۰-۹0-9]+[\.\-]\s+)', content)
    
    for b in blocks:
        m_link = re.search(r'https?://[^\s\n]+/reel/([A-Za-z0-9_-]+)/?', b)
        if not m_link:
            m_link = re.search(r'https?://[^\s\n]+/(?:p|reels)/([A-Za-z0-9_-]+)/?', b)
        if not m_link:
            continue
            
        code = m_link.group(1)
        full_url = m_link.group(0)
        
        m_views = re.search(r'(?:آمار|ویو|بازدید|views)[^\n:]*[:\s]+([^\n]+)', b, re.IGNORECASE)
        views_str = m_views.group(1).strip() if m_views else ''
        
        m_text = re.search(r'[«"]([^»"]+)[»"]', b)
        if not m_text:
            m_text = re.search(r'```text\n(.*?)```', b, re.DOTALL)
            
        txt = m_text.group(1).strip() if m_text else ''
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        line_count = len(lines)
        
        is_1m = ('میلیون' in views_str or 'M' in views_str or any(k in views_str for k in ['1,', '2,', '3,', '4,', '5,', '6,', '7,', '8,', '9,', '10,'])) and not any(k in views_str for k in ['0.', '۰٫'])
        
        if is_1m:
            in_db = code in db_codes or full_url in db_urls
            res_hist = ENGINE.check_duplicate_against_history(lines[0] if lines else '', txt) if txt else {'is_duplicate': False, 'similarity_score': 0}
            print(f"[{code}] Views: {views_str} | Lines: {line_count} | InDB: {in_db} | HistDup: {res_hist['is_duplicate']} ({res_hist['similarity_score']}%)")
