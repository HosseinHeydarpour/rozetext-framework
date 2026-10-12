import os
import re
import json
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

# Search all files in D:\rozetext-framework and D:\rozetext content
search_dirs = [r'd:\rozetext-framework', r'd:\rozetext content']
candidates = {}

for s_dir in search_dirs:
    for root, dirs, files in os.walk(s_dir):
        if '.git' in root or '__pycache__' in root or 'node_modules' in root:
            continue
        for f in files:
            if not (f.endswith('.txt') or f.endswith('.json') or f.endswith('.py') or f.endswith('.md')):
                continue
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fl:
                    content = fl.read()
                
                # find instagram reel links
                for m in re.finditer(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', content):
                    code = m.group(1)
                    if code.lower() in db_codes or code.lower() in candidates or len(code) < 5:
                        continue
                    
                    # extract text around m
                    start = max(0, m.start() - 300)
                    end = min(len(content), m.end() + 1200)
                    chunk = content[start:end]
                    
                    # check views
                    m_v = re.search(r'(\d+[\.,]?\d*\s*[Mm]|\d+,\d+,\d+\s*بازدید|\d+[\.,]?\d*\s*میلیون)', chunk)
                    # check page
                    m_p = re.search(r'(@[A-Za-z0-9_\.]+|[A-Za-z0-9_\.]+\.ir)', chunk)
                    page = m_p.group(1) if m_p else "@unknown"
                    if 'halekhoub' in page.lower():
                        continue
                        
                    # find code block or verbatim text
                    m_t = re.search(r'```(?:text)?\s*([\s\S]*?)```', chunk)
                    if not m_t:
                        m_t = re.search(r'متن دقیق.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n-|\n\s*متن|$)', chunk)
                    
                    text_cand = m_t.group(1).strip() if m_t else ""
                    lines = [l.strip() for l in text_cand.split('\n') if l.strip()]
                    
                    if m_v and len(lines) >= 6:
                        dup = engine.check_duplicate_against_history(text_cand, text_cand)
                        if not dup['is_duplicate']:
                            candidates[code.lower()] = {
                                'code': code,
                                'url': m.group(0),
                                'page': page,
                                'views': m_v.group(1),
                                'lines': len(lines),
                                'sim': dup['similarity_score'],
                                'text': text_cand,
                                'file': fp
                            }
            except Exception:
                pass

print(f"Total fresh verified candidates found across Drive D: {len(candidates)}")
for i, (k, c) in enumerate(candidates.items()):
    print(f"{i+1}. [{c['views']}] {c['code']} ({c['page']}) -> Sim={c['sim']}% | lines={c['lines']} | Hook: {c['text'].split(chr(10))[0][:35]} (file: {os.path.basename(c['file'])})")
