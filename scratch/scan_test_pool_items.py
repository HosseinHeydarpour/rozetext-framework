import sys, os, json, re
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('./scratch'))
sys.stdout.reconfigure(encoding='utf-8')
from server import PublisherEngine
import test_pool

engine = PublisherEngine()

items = test_pool.pool + test_pool.verified_additional
print('Total items in test_pool:', len(items))

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

def parse_views(v_str):
    v_str = str(v_str)
    # Check for M / میلیون
    m_M = re.search(r'([\d\.]+)\s*(?:M|میلیون)', v_str, re.IGNORECASE)
    if m_M:
        try:
            return int(float(m_M.group(1)) * 1000000)
        except:
            pass
    # Check for raw numbers with commas
    clean = v_str.replace(',', '').replace('٬', '')
    digits = re.findall(r'\d+', clean)
    for d in digits:
        val = int(d)
        if val >= 500000: # large number like 1600000
            return val
    return 0

cands = []
for it in items:
    url = it.get('source_url', '').strip()
    views_str = str(it.get('source_views', ''))
    v_num = parse_views(views_str)

    txt = it.get('content', '') or it.get('extracted_raw_text', '')
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    dup = engine.check_duplicate_against_history(txt, txt)
    
    if v_num >= 1000000:
        cands.append({
            'url': url,
            'page': it.get('source_page'),
            'views_str': views_str,
            'views_num': v_num,
            'lines': len(lines),
            'in_db': url in db_urls,
            'is_dup': dup['is_duplicate'],
            'sim': dup['similarity_score'],
            'hook': lines[0] if lines else '',
            'item': it
        })

print(f'Items with >=1M views: {len(cands)}')
for c in cands:
    print(f"- [{c['views_num']:,}] {c['page']} | L:{c['lines']} | inDB:{c['in_db']} | Dup:{c['is_dup']}({c['sim']:.1f}%) | {c['url']}")
    print(f"   Hook: {c['hook']}")
