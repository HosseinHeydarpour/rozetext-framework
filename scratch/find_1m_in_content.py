import os, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Collect existing db texts & used urls/codes
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

# The 9 already verified reels
verified_9_codes = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DNTYt15oqYj', 'DZSr1vMN1mr',
    'DPjI0mTCIPs', 'DKm6Qn6I9vQ', 'DQHm9z6CMeL', 'DPRj9ddCF5T', 'DbyY0F7tmAn'
}

files = [
    r'D:\rozetext content\top_50_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt'
]

def parse_file(fp):
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    
    # Split by entries like "۱. پیج" or "\n\d+\. پیج" or "\n\d+\. "
    items = re.split(r'\n(?=\d+\.\s+پیج|\d+\.\s+@)', text)
    parsed = []
    for item in items:
        # Extract link
        m_link = re.search(r'لینک:\s*(https?://[^\s\n]+)', item)
        m_views = re.search(r'آمار:\s*([^\n]+)', item)
        m_page = re.search(r'(?:پیج\s*|@)([a-zA-Z0-9_.]+)', item)
        
        # Extract text: between « and » or after "متن دقیق"
        m_text = re.search(r'«([^»]+)»', item)
        if not m_text:
            m_text = re.search(r'متن دقیق[^\n]*\n(.*?)(?=\n-|\n===|\n\d+\.|$)', item, re.DOTALL)
            
        if m_link and m_views and m_text:
            link = m_link.group(1).strip()
            views_str = m_views.group(1).strip()
            raw_text = m_text.group(1).strip()
            page = m_page.group(1).strip() if m_page else ''
            
            # Extract code
            m_c = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', link)
            code = m_c.group(1) if m_c else ''
            
            parsed.append({
                'code': code,
                'link': link,
                'views_str': views_str,
                'page': page,
                'raw_text': raw_text
            })
    return parsed

all_items = []
seen_codes = set()
for fp in files:
    items = parse_file(fp)
    for it in items:
        if it['code'] and it['code'] not in seen_codes:
            seen_codes.add(it['code'])
            all_items.append(it)

print(f"Total parsed reels from text files: {len(all_items)}")

# Now filter
valid_1m_candidates = []

for it in all_items:
    code = it['code']
    views = it['views_str']
    txt = it['raw_text']
    
    # Must be 1M+
    is_1m = ('میلیون' in views or 'M' in views or '10,' in views or '1,' in views) and not ('۰.' in views or '0.' in views)
    if not is_1m:
        continue
        
    # Must not be used in db
    if code in used_codes:
        continue
        
    # Must not be in verified 9
    if code in verified_9_codes:
        continue
        
    # Check lines 7..16
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if len(lines) < 7 or len(lines) > 16:
        continue
        
    # Check persona blacklist
    if '@halekhoub' in it['page'] or 'halekhoub' in it['page']:
        continue
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    if any(bw in txt for bw in bad_words):
        continue
        
    # Anti-duplication vs history
    res_hist = ENGINE.check_duplicate_against_history(lines[0], txt)
    if res_hist['is_duplicate']:
        print(f"Skipping {code}: duplicate of history Reel #{res_hist.get('duplicate_of_reel')} ({res_hist['similarity_score']}%)")
        continue
        
    # Anti-duplication vs db
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
        
    valid_1m_candidates.append(it)

print(f"\n================ VALID CLEAN 1M+ CANDIDATES: {len(valid_1m_candidates)} ================")
for c in valid_1m_candidates:
    lines = [l.strip() for l in c['raw_text'].splitlines() if l.strip()]
    print(f"\n[{c['code']}] Page: @{c['page']} | Views: {c['views_str']} | Lines: {len(lines)}")
    print(f"Link: {c['link']}")
    print(f"Hook: {lines[0]}")
    print(f"Text:\n{c['raw_text']}")
