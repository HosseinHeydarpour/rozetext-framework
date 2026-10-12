import json, sys, re, os
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

items = raw.split('--------------------------------------------------------------------------------')
print(f'Total items: {len(items)}')

candidates = []

for i, it in enumerate(items):
    m = re.search(r'متن ویدیو:\s*\n[«"]?(.*?)[»"]?\s*\n-\s*ریز', it, re.DOTALL)
    if not m:
        # fallback search
        m = re.search(r'متن ویدیو:\s*\n[«"]?(.*?)[»"]?\s*\n-', it, re.DOTALL)
    if m:
        txt = m.group(1).strip()
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        url_m = re.search(r'https://[^\s\n]+', it)
        url = url_m.group(0).rstrip('/') if url_m else ''
        code = url.split('/')[-1] if url else ''
        views_m = re.search(r'آمار:\s*([^\n]+)', it)
        views = views_m.group(1) if views_m else ''
        
        # Check views 1M+
        is_1m = ('میلیون' in views or 'M' in views or '۲٬' in views or '۳٬' in views or '۱٬' in views or '۴٬' in views or '۵٬' in views)
        if not is_1m:
            continue
            
        if code in db_codes:
            continue
            
        hist = ENGINE.check_duplicate_against_history(txt, txt)
        
        c_tokens = ENGINE._normalize_persian_tokens(txt)
        max_dbsim = 0
        for dbt in db_texts:
            dbt_tokens = ENGINE._normalize_persian_tokens(dbt)
            sim = len(c_tokens & dbt_tokens) / max(1, min(len(c_tokens), len(dbt_tokens)))
            if sim > max_dbsim:
                max_dbsim = sim
                
        print(f"Item #{i} [{code}] ({views}) | Lines: {len(lines)} | HistDup: {hist['is_duplicate']} ({hist['similarity_score']:.1f}%) | DBSim: {max_dbsim:.1%}")
        print(f"  Hook: {lines[0] if lines else 'EMPTY'}")
        if len(lines) >= 6 and not hist['is_duplicate'] and max_dbsim < 0.40:
            candidates.append({
                'code': code,
                'url': url,
                'views': views,
                'lines': len(lines),
                'hook': lines[0],
                'text': txt,
                'hist_sim': hist['similarity_score'],
                'db_sim': max_dbsim
            })

print(f'\n=== FOUND {len(candidates)} LONG TEXT QUALIFYING CANDIDATES ===\n')
for c in candidates:
    print(f"[{c['code']}] {c['views']} | Lines: {c['lines']}")
    print(c['text'])
    print('-'*50)
