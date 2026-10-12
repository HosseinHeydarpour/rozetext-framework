import os, glob, sys, re, json
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

verified_5 = {'DNTYt15oqYj', 'DZDRxCkNgjw', 'DbyY0F7tmAn', 'DPRj9ddCF5T', 'DKm6Qn6I9vQ', 'C5WPI8OCK4x'}

review_files = glob.glob(r'C:\Users\User\.gemini\antigravity\brain\727a329c-ae5d-47f3-930f-a557f52abe67\*.md')
print(f"Scanning {len(review_files)} review files...")

found_reels = []

for rf in review_files:
    fname = os.path.basename(rf)
    with open(rf, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Let's split by reel sections, e.g. ## Reel or ### Reel or similar
    sections = re.split(r'\n(?=#{1,4}\s+)', content)
    for sec in sections:
        m_link = re.search(r'https?://[^\s\n\)]+/(?:p|reel|reels)/([A-Za-z0-9_-]+)', sec)
        if not m_link:
            continue
        code = m_link.group(1)
        url = m_link.group(0)
        
        m_views = re.search(r'(?:views|بازدید|ویو)[^\n:]*[:\s]+([^\n]+)', sec, re.IGNORECASE)
        views_str = m_views.group(1).strip() if m_views else ''
        
        m_text = re.search(r'```(?:text)?\n(.*?)```', sec, re.DOTALL)
        if not m_text:
            m_text = re.search(r'>\s*(.*?)(?=\n\n|\n[#\-]|\Z)', sec, re.DOTALL)
            
        if not m_text:
            continue
            
        txt = m_text.group(1).strip()
        txt = re.sub(r'^[>\s]+', '', txt, flags=re.MULTILINE)
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        line_count = len(lines)
        
        is_1m = ('میلیون' in views_str or 'M' in views_str or any(k in views_str for k in ['1,', '2,', '3,', '4,', '5,', '6,', '7,', '8,', '9,', '10,'])) and not any(k in views_str for k in ['0.', '۰٫'])
        
        in_db = code in db_codes or url in db_urls
        in_v = code in verified_5
        
        res_hist = ENGINE.check_duplicate_against_history(txt, txt)
        
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
        has_bad = any(bw in txt for bw in bad_words)
        
        if is_1m and 7 <= line_count <= 16 and not in_db and not in_v and not db_dup and not res_hist['is_duplicate'] and not has_bad:
            print(f"Found in {fname}: [{code}] Views: {views_str} | Lines: {line_count}")
            print(f"   Hook: {lines[0]}")
            print(f"   Text:\n{txt}\n")
            found_reels.append({
                'code': code,
                'url': url,
                'views': views_str,
                'lines': line_count,
                'text': txt,
                'file': fname
            })

print(f"\nTOTAL CLEAN QUALIFIED FROM REVIEW FILES: {len(found_reels)}")
