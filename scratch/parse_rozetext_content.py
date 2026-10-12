import glob
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load existing DB codes
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c)

print(f"Existing DB codes: {len(db_codes)}")

files = glob.glob(r'D:\rozetext content\*.txt')
all_posts = []

for fp in files:
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            text = f.read()
            # Split by divider or post number
            blocks = re.split(r'-{30,}|={30,}', text)
            for b in blocks:
                if 'instagram.com/reel' not in b:
                    continue
                # Extract link
                m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
                if not m_url:
                    continue
                code = m_url.group(1)
                if code in db_codes:
                    continue
                
                # Extract views
                m_views = re.search(r'([\d\.,\s]+(?:میلیون|ویو|لایک|[Mm]))', b)
                # Extract text
                m_text = re.search(r'متن ویدیو:\s*«?([\s\S]*?)»?\s*(?:- ریز امتیازات|\n\s*-|$)', b)
                raw_text = m_text.group(1).strip() if m_text else ""
                lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                
                # Extract account/page
                m_page = re.search(r'([A-Za-z0-9_\.]+\.ir|@[A-Za-z0-9_\.]+)', b)
                page = m_page.group(1) if m_page else "@unknown"
                
                all_posts.append({
                    'code': code,
                    'url': m_url.group(0),
                    'views_raw': b[:150],
                    'page': page,
                    'text': raw_text,
                    'lines_count': len(lines),
                    'file': fp
                })
    except Exception as e:
        print(f"Error reading {fp}: {e}")

print(f"Total fresh reels parsed from 'D:\\rozetext content': {len(all_posts)}")
for p in all_posts[:20]:
    print(f"Code: {p['code']} | Lines: {p['lines_count']} | Page: {p['page']} | Text snippet: {p['text'][:60]}")
