import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import ENGINE

with open('scratch/subagent_12_reels_full.txt', 'r', encoding='utf-8') as f:
    text = f.read()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))
existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), txt.strip()))

reels_raw = re.split(r'###\s+\d+\.', text)
print(f"Total sections found: {len(reels_raw)}")

clean_candidates = []

for i, sec in enumerate(reels_raw[1:], 1):
    m_url = re.search(r'https://www\.instagram\.com/reel/([A-Za-z0-9_-]+)/', sec)
    m_views = re.search(r'\*\*بازدید[^\*]*\*\*[:\s]*\*\*?([^\n\*]+)', sec)
    m_txt = re.search(r'```text\n(.*?)```', sec, re.DOTALL)
    url = m_url.group(0) if m_url else 'N/A'
    shortcode = m_url.group(1) if m_url else 'N/A'
    views = m_views.group(1).strip() if m_views else 'N/A'
    body = m_txt.group(1).strip() if m_txt else ''
    lines = [l.strip() for l in body.splitlines() if l.strip()]
    
    if not body:
        continue
        
    dup_hist = ENGINE.check_duplicate_against_history(body, body)
    
    # Check DB duplicate
    c_tokens = ENGINE._normalize_persian_tokens(body)
    c_ngrams = ENGINE._extract_ngrams(body, 4)
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
            
    in_db = url in db_urls
    
    print(f"Reel {i}: {shortcode} | Views: {views} | Lines: {len(lines)}")
    print(f"  URL: {url}")
    print(f"  In DB: {in_db} | DB Dup: {db_dup} (Closest: {closest_db})")
    print(f"  Hist Dup: {dup_hist['is_duplicate']} (sim={dup_hist.get('similarity_score', 0):.1f}%) | Closest: {dup_hist.get('duplicate_of_reel')}")
    print(f"  First line: {lines[0] if lines else 'None'}")
    print("-" * 50)
    
    if not in_db and not db_dup and not dup_hist['is_duplicate'] and 7 <= len(lines) <= 16:
        clean_candidates.append({
            'shortcode': shortcode,
            'url': url,
            'views': views,
            'lines': len(lines),
            'body': body
        })

print(f"\nTOTAL CLEAN NON-DUPLICATES: {len(clean_candidates)}")
for c in clean_candidates:
    print(f"  - [{c['shortcode']}] {c['views']} ({c['lines']} lines): {c['body'].splitlines()[0]}")
