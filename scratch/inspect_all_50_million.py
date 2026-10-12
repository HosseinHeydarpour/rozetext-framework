import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')

from server import PublisherEngine
engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c.lower())

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8') as f:
    text = f.read()

items = re.split(r'\n(?=\d+[\.\،]\s*پیج)', text)
for b in items:
    m_head = re.search(r'(\d+)[\.\،]\s*پیج\s*([^\n\r]+)', b)
    if not m_head:
        continue
    num = m_head.group(1)
    page = m_head.group(2).strip()
    
    m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
    if not m_url:
        continue
    code = m_url.group(1)
    
    m_views = re.search(r'آمار:\s*([^\n\r]+)', b)
    views_str = m_views.group(1).strip() if m_views else ""
    
    is_million = False
    if 'میلیون' in views_str or 'M' in views_str or 'm' in views_str:
        is_million = True
    else:
        digits = re.findall(r'[\d٬,]+', views_str)
        for d in digits:
            nd = d.replace('٬', '').replace(',', '').replace('۰', '0').replace('۱', '1').replace('۲', '2').replace('۳', '3').replace('۴', '4').replace('۵', '5').replace('۶', '6').replace('۷', '7').replace('۸', '8').replace('۹', '9')
            if nd.isdigit() and int(nd) >= 1000000:
                is_million = True
                break
                
    m_text = re.search(r'متن دقیق داخل ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|$)', b)
    if not m_text:
        m_text = re.search(r'متن ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|$)', b)
    
    raw_text = m_text.group(1).strip() if m_text else ""
    raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    
    in_db = code.lower() in db_codes
    dup = engine.check_duplicate_against_history(raw_text, raw_text) if raw_text else {'is_duplicate': True, 'similarity_score': 0}
    
    if is_million and not in_db and len(lines) >= 6:
        print(f"#{num} [{views_str}] {code} ({page}) -> is_dup={dup['is_duplicate']} (sim={dup['similarity_score']}%) | lines={len(lines)} | match: {dup.get('duplicate_of_reel')} «{dup.get('matched_hook', '')[:30]}»")
