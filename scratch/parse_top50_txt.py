import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Split by items
items = re.split(r'\n(?=\d+\.\s*\[|#\s*\d+|\bرتبه\s*\d+)', text)
print(f"Total blocks in top_50_viral_delneveshte_reels.txt: {len(items)}")

candidates = []
for b in items:
    m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
    if not m_url:
        continue
    url = m_url.group(0)
    code = m_url.group(1)
    
    # Views
    m_v = re.search(r'(?:آمار|ویو|بازدید|views)[\s:]*([^\n\r]+)', b, re.IGNORECASE)
    v_str = m_v.group(1) if m_v else ""
    
    is_million = False
    if 'میلیون' in v_str or 'M' in v_str or 'm' in v_str:
        is_million = True
    else:
        digits = re.findall(r'[\d٬,]+', v_str)
        for d in digits:
            norm_d = d.replace('٬', '').replace(',', '').replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')
            if norm_d.isdigit() and int(norm_d) >= 1000000:
                is_million = True
                break
    
    m_text = re.search(r'متن(?: دقیق)?(?: داخل)? ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|\n\s*کپشن|$)', b)
    raw_text = m_text.group(1).strip() if m_text else ""
    raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    
    dup = engine.check_duplicate_against_history(raw_text, raw_text) if raw_text else {'is_duplicate': False, 'similarity_score': 0}
    in_db = url in db_urls or code in str(db_urls)
    
    if is_million and len(lines) >= 6:
        candidates.append({
            'code': code,
            'url': url,
            'views_str': v_str,
            'lines': len(lines),
            'in_db': in_db,
            'is_dup': dup['is_duplicate'],
            'sim': dup['similarity_score'],
            'raw_text': raw_text
        })

print(f"Candidates with >=1M and >=6 lines: {len(candidates)}")
for c in candidates:
    print(f"- {c['code']} | Views: {c['views_str']} | L:{c['lines']} | inDB:{c['in_db']} | Dup:{c['is_dup']} ({c['sim']:.1f}%)")
    print(f"   Hook: {c['raw_text'].splitlines()[0][:60]}")
