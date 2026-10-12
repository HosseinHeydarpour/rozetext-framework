import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

p = r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\new_top_50_reels.json'
with open(p, 'r', encoding='utf-8') as f:
    raw = json.loads(f.read())

# Split by reel sections
sections = re.split(r'### |\n(?=\d+\.\s+پیج|\d+\.\s+ریلز)', raw)
print(f'Total sections: {len(sections)}')

valid_1m_reels = []

for sec in sections:
    url_m = re.search(r'https://www\.instagram\.com/reel/([A-Za-z0-9_-]+)/', sec)
    if not url_m:
        continue
    code = url_m.group(1)
    url = f'https://www.instagram.com/reel/{code}/'
    
    # Views
    views_m = re.search(r'(?:آمار|ویو|بازدید).*?([0-9\.,]+|\d+)\s*(?:M|میلیون|k|K|ویو|لایک)', sec)
    views_str = views_m.group(0) if views_m else ''
    
    # Check if 1M+
    is_1m = ('میلیون' in sec or 'M' in sec or '2,' in sec or '3,' in sec or '1,' in sec or '4,' in sec or '5,' in sec)
    if not is_1m:
        continue
        
    # Page
    page_m = re.search(r'پیج\s*([@A-Za-z0-9_\.]+)', sec)
    page = page_m.group(1) if page_m else ''
    if not page.startswith('@'):
        page = '@' + page
        
    # Text
    # Extract text after "متن ویدیو:" or "متن:"
    txt_m = re.search(r'(?:متن ویدیو|متن|متن روی ویدیو|اسکریپت):\s*\n(.*?)(?=\n- |\n\n\n|\n[۰-۹0-9]+\.|$)', sec, re.DOTALL)
    if not txt_m:
        continue
    txt = txt_m.group(1).strip()
    # Clean markdown quotes or code blocks
    txt = re.sub(r'```[a-z]*\n|```', '', txt).strip()
    txt = '\n'.join([l.strip().lstrip('«"\'').rstrip('»"\'') for l in txt.splitlines() if l.strip()])
    
    lines = [l for l in txt.splitlines() if l]
    if not (7 <= len(lines) <= 16):
        continue
        
    if code in db_codes:
        continue
        
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    if hist['is_duplicate']:
        continue
        
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    db_dup = False
    max_dbsim = 0
    for dbt in db_texts:
        dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
        sim = len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens)))
        if sim > max_dbsim:
            max_dbsim = sim
        if sim >= 0.40:
            db_dup = True
            break
    if db_dup:
        continue
        
    valid_1m_reels.append({
        'code': code,
        'url': url,
        'page': page,
        'views_str': views_str,
        'lines_count': len(lines),
        'hook': lines[0],
        'text': txt,
        'hist_sim': hist['similarity_score'],
        'db_sim': max_dbsim
    })

print(f'\n================ FOUND {len(valid_1m_reels)} QUALIFYING 1M+ REELS ================\n')
for r in valid_1m_reels:
    print(f"[{r['code']}] {r['page']} | {r['views_str']} | Lines: {r['lines_count']} | HistSim: {r['hist_sim']:.1f}% | DBSim: {r['db_sim']:.1%}")
    print(f"Hook: {r['hook']}")
    print("Text:\n" + r['text'])
    print("-" * 60)
