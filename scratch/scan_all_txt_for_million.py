import json
import os
import re
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from server import PublisherEngine
engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c)

print(f"DB existing codes: {len(db_codes)}")

# Let's inspect all txt files in D:/rozetext content
txt_files = glob.glob(r'D:\rozetext content\*.txt')

all_found = []

for fp in txt_files:
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Try different split strategies
    # 1. Regex find all instagram reel URLs and grab surrounding text
    matches = list(re.finditer(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', content))
    for i, m in enumerate(matches):
        code = m.group(1)
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(content)
        block = content[start:end]
        
        # Check views
        m_views = re.search(r'(?:آمار|ویو|بازدید|views)[\s:]*([^\n\r]+)', block, re.IGNORECASE)
        views_str = m_views.group(1) if m_views else ""
        
        # Also search nearby text before start (up to 300 chars back)
        pre_text = content[max(0, start-300):start]
        if not views_str:
            m_pre_views = re.search(r'(?:آمار|ویو|بازدید|views)[\s:]*([^\n\r]+)', pre_text, re.IGNORECASE)
            if m_pre_views:
                views_str = m_pre_views.group(1)
                
        # Determine views count
        is_million = False
        views_val = 0
        if 'میلیون' in views_str or 'M' in views_str or 'm' in views_str:
            is_million = True
            m_num = re.search(r'([\d\.]+)', views_str.replace('٬', '').replace(',', ''))
            if m_num:
                try:
                    views_val = float(m_num.group(1)) * 1000000
                except:
                    pass
        else:
            digits = re.findall(r'[\d٬,]+', views_str)
            for d in digits:
                norm_d = d.replace('٬', '').replace(',', '').replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')
                if norm_d.isdigit() and int(norm_d) >= 1000000:
                    is_million = True
                    views_val = int(norm_d)
                    break
        
        # Check page
        m_page = re.search(r'(?:پیج|page)[\s:]*([A-Za-z0-9_\.]+|@[A-Za-z0-9_\.]+)', block, re.IGNORECASE)
        if not m_page:
            m_page = re.search(r'(?:پیج|page)[\s:]*([A-Za-z0-9_\.]+|@[A-Za-z0-9_\.]+)', pre_text, re.IGNORECASE)
        page = m_page.group(1) if m_page else ""
        
        # Extract raw text
        m_text = re.search(r'متن(?: دقیق)?(?: داخل)? ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|\n\s*کپشن|$)', block)
        raw_text = m_text.group(1).strip() if m_text else ""
        raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        
        all_found.append({
            'code': code,
            'url': m.group(0),
            'file': os.path.basename(fp),
            'views_str': views_str,
            'is_million': is_million,
            'views_val': views_val,
            'page': page,
            'lines_count': len(lines),
            'raw_text': raw_text,
            'in_db': code in db_codes
        })

print(f"Total reels parsed across all txt files: {len(all_found)}")
# Filter unique by code
unique = {}
for r in all_found:
    if r['code'] not in unique or (r['is_million'] and not unique[r['code']]['is_million']):
        unique[r['code']] = r

print(f"Unique reels: {len(unique)}")
m_reels = [r for r in unique.values() if r['is_million']]
print(f"Million+ reels: {len(m_reels)}")

for r in m_reels:
    dup = engine.check_duplicate_against_history(r['raw_text'], r['raw_text']) if r['raw_text'] else {'is_duplicate': False, 'similarity_score': 0}
    r['dup'] = dup
    print(f"- {r['code']} | {r['file']} | {r['page']} | Views: {r['views_str']} | Lines: {r['lines_count']} | InDB: {r['in_db']} | Dup: {dup['is_duplicate']} ({dup['similarity_score']:.1f}%)")
    if r['lines_count'] > 0:
        print(f"   Hook: {r['raw_text'].splitlines()[0][:60]}")
