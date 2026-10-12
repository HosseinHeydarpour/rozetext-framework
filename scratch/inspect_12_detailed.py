import json
import os
import re
import sys

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

files = [
    r'D:\rozetext content\top_50_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt',
    r'D:\rozetext content\top_15_viral_delneveshte_reels.txt'
]

candidates = []

for fp in files:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n-+\n|\n=+\n', content)
    for b in blocks:
        if 'instagram.com/reel' not in b:
            continue
        m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
        if not m_url:
            continue
        code = m_url.group(1)
        if code in db_codes or any(c['code'] == code for c in candidates):
            continue
        
        m_views = re.search(r'آمار:\s*([^\n\r]+)', b)
        views_str = m_views.group(1) if m_views else ""
        
        is_million = False
        if 'میلیون' in views_str or 'M' in views_str or 'm' in views_str:
            is_million = True
        else:
            digits = re.findall(r'[\d٬,]+', views_str)
            for d in digits:
                norm_d = d.replace('٬', '').replace(',', '').replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')
                if norm_d.isdigit() and int(norm_d) >= 1000000:
                    is_million = True
                    break
        
        if not is_million:
            continue
        
        m_page = re.search(r'پیج\s*([A-Za-z0-9_\.]+|@[A-Za-z0-9_\.]+)', b)
        page = m_page.group(1) if m_page else ""
        if 'halekhoub' in page.lower():
            continue
        
        m_text = re.search(r'متن دقیق داخل ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|$)', b)
        if not m_text:
            m_text = re.search(r'متن ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|$)', b)
        
        raw_text = m_text.group(1).strip() if m_text else ""
        raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        
        if not (6 <= len(lines) <= 18):
            continue
        
        if 'مولانا' in raw_text or 'شمس' in raw_text:
            continue
            
        m_topic = re.search(r'موضوع:\s*([^\n\r]+)', b)
        topic = m_topic.group(1).strip() if m_topic else ""
        
        m_cap = re.search(r'متن دقیق کپشن:\s*«?([^\n\r»]+)»?', b)
        cap = m_cap.group(1).strip() if m_cap else ""
        
        # Anti-duplication check against published-content-history.md
        dup_check = engine.check_duplicate_against_history(raw_text, raw_text)
        
        candidates.append({
            'code': code,
            'url': m_url.group(0),
            'page': page if page.startswith('@') else (f"@{page}" if page else "@unknown"),
            'views': views_str,
            'lines_count': len(lines),
            'text': raw_text,
            'caption': cap,
            'topic': topic,
            'file': fp,
            'dup_check': dup_check
        })

print(f"Total candidates: {len(candidates)}")
for i, c in enumerate(candidates):
    print(f"\n================ REEL #{i+1} [{c['code']}] ================")
    print(f"URL: {c['url']}")
    print(f"Page: {c['page']} | Views: {c['views']}")
    print(f"Topic: {c['topic']}")
    print(f"Lines count: {c['lines_count']}")
    print(f"Duplicate check: is_dup={c['dup_check']['is_duplicate']} (sim={c['dup_check']['similarity_score']}%)")
    print("--- IN-VIDEO VERBATIM TEXT ---")
    print(c['text'])
