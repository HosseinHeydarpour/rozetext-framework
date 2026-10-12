import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_db_texts = []
for s in db.get('scripts', []):
    t = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if t.strip():
        existing_db_texts.append(t.strip())

with open('reports/06-10-2026-report.md', 'r', encoding='utf-8') as f:
    text = f.read()

blocks = re.split(r'\nReel #\d+', text)
print(f"Total blocks split: {len(blocks)}")

clean_candidates = []

for b in blocks[1:]:
    # Extract ID
    m_id = re.search(r'• Reel ID:\s*([A-Za-z0-9_-]+)', b)
    m_url = re.search(r'• URL:\s*(https://[^\s]+)', b)
    m_views = re.search(r'• Views:\s*([\d,]+)', b)
    m_cap = re.search(r'• Caption:\s*(.*?)(?=\n• Manual Content:)', b, re.DOTALL)
    m_content = re.search(r'• Manual Content:\s*(.*?)(?=\n• AI Prediction:|\Z)', b, re.DOTALL)
    
    if not (m_id and m_url and m_views and m_content):
        continue
        
    rid = m_id.group(1).strip()
    url = m_url.group(1).strip()
    views_val = int(m_views.group(1).replace(',', ''))
    raw_content = m_content.group(1).strip()
    caption = m_cap.group(1).strip() if m_cap else ""
    
    if views_val < 1000000:
        continue
        
    lines = [l.strip() for l in raw_content.splitlines() if l.strip()]
    if len(lines) < 7 or len(lines) > 16:
        continue
        
    bad_words = ['مولانا', 'شمس', 'دختر', 'پسر', 'تولد', 'نوروز', 'یلدا']
    if any(bw in raw_content for bw in bad_words):
        continue
        
    res_hist = ENGINE.check_duplicate_against_history(raw_content, raw_content)
    if res_hist['is_duplicate']:
        continue
        
    c_tokens = ENGINE._normalize_persian_tokens(raw_content)
    c_ngrams = ENGINE._extract_ngrams(raw_content, 4)
    db_dup = False
    for dbt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(dbt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(dbt, 4)
        common_ngrams = c_ngrams & s_ngrams
        if len(common_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            break
    if db_dup:
        continue
        
    clean_candidates.append({
        'shortcode': rid,
        'url': url,
        'views': views_val,
        'views_str': f"{views_val:,} بازدید ({views_val/1000000:.1f}M)",
        'lines': len(lines),
        'content': raw_content,
        'caption': caption,
        'hook': lines[0]
    })

print(f"\n================ CLEAN 1M+ REELS IN REPORT: {len(clean_candidates)} ================\n")
for c in clean_candidates:
    print(f"[{c['shortcode']}] Views: {c['views_str']} | Lines: {c['lines']} | Hook: {c['hook']}")
