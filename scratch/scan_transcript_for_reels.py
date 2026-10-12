import sys, os, json, re
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

found_reels = {}

if os.path.exists(transcript_path):
    print("Reading transcript_full.jsonl...")
    with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f):
            if not ('instagram.com/reel' in line or 'instagram.com/p/' in line):
                continue
            
            # find all urls
            urls = re.findall(r'https?://(?:www\.)?instagram\.com/(?:reel|p)/([A-Za-z0-9_-]+)/?', line)
            for code in urls:
                if code in found_reels:
                    continue
                # find context around code
                idx = line.find(code)
                ctx = line[max(0, idx - 400):min(len(line), idx + 1500)]
                
                # look for views
                m_v = re.search(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', ctx)
                m_digits = re.findall(r'[\d,٬]{7,}', ctx)
                
                views_str = ""
                is_1m = False
                if m_v and '0.' not in m_v.group(1):
                    views_str = m_v.group(1)
                    is_1m = True
                elif m_digits:
                    views_str = m_digits[0]
                    is_1m = True
                
                if is_1m:
                    found_reels[code] = (views_str, ctx)

print(f"Total 1M+ reel codes found in transcript: {len(found_reels)}")
for code, (v, ctx) in found_reels.items():
    print(f"- {code} | views: {v}")
