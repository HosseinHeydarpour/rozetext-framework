import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

p_full = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'
p_compact = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript.jsonl'

# Load existing DB codes
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c)

# Read compact transcript lines first
candidates = {}

for path in [p_compact, p_full]:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'instagram.com/reel' not in line:
                    continue
                # Search for reel codes
                codes = re.findall(r'instagram\.com/reel[s]?/([A-Za-z0-9_-]+)', line)
                for code in codes:
                    if code in db_codes or len(code) < 5 or code in ['TEST99', 'VIRAL']:
                        continue
                    if code not in candidates:
                        candidates[code] = []
                    candidates[code].append(line)
    except Exception as e:
        print(f"Error reading {path}: {e}")

print(f"Unique fresh candidates: {len(candidates)}")

# For each candidate, extract view count, page, text if present
results = []
for code, lines in candidates.items():
    combined_text = "\n".join(lines)
    
    # search views
    views_matches = re.findall(r'(\d+[\.,]?\d*\s*[Mm]|[\d,]{7,}\s*بازدید|\d+[\.,]?\d*\s*میلیون)', combined_text)
    
    # search page
    page_matches = re.findall(r'(@[A-Za-z0-9_\.]+)', combined_text)
    
    # search persian block / text
    results.append({
        'code': code,
        'views': views_matches[0] if views_matches else 'Unknown',
        'page': page_matches[0] if page_matches else '@unknown',
        'occurrences': len(lines)
    })

for r in results[:30]:
    print(f"Code: {r['code']} | Views: {r['views']} | Page: {r['page']} | Mentions: {r['occurrences']}")
