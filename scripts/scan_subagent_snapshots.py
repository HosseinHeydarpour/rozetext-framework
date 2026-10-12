import os, sys, glob, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = {s.get('source_url', '').rstrip('/').split('/')[-1] for s in db['scripts'] if s.get('source_url')}
db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

folder = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.tempmediaStorage'
files = glob.glob(os.path.join(folder, '*.txt'))

# Let's inspect each snapshot for reel URLs with views and Persian text
results = []

for fpath in files:
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [l.strip() for l in f if l.strip()]
    except Exception:
        continue
        
    full_text = '\n'.join(lines)
    
    # Find all reel links
    # In accessibility trees, reels often look like:
    # link "reel ... 1.2M plays" or link "... /reel/CODE/ ..."
    for i, line in enumerate(lines):
        if '/reel/' in line or '/reels/' in line:
            m = re.search(r'(?:reel/|reels/)([A-Za-z0-9_-]{11})', line)
            if not m:
                continue
            code = m.group(1)
            if code in db_codes:
                continue
                
            # Look around line i for views
            window = '\n'.join(lines[max(0, i-5):min(len(lines), i+15)])
            views_m = re.search(r'([0-9\.,]+|\d+)\s*(?:M|میلیون|M plays|plays)', window, re.IGNORECASE)
            views = views_m.group(0) if views_m else ''
            
            # Check if 1M+
            if views and not views.startswith('0.') and ('M' in views or 'میلیون' in views):
                results.append({
                    'code': code,
                    'file': os.path.basename(fpath),
                    'views': views,
                    'line': line,
                    'window': window
                })

print(f'Total 1M+ occurrences found: {len(results)}')
unique_1m = {}
for r in results:
    if r['code'] not in unique_1m:
        unique_1m[r['code']] = r

print(f'Unique 1M+ reel codes: {len(unique_1m)}')
for code, r in list(unique_1m.items())[:30]:
    print(f"[{code}] Views: {r['views']} | File: {r['file']}")
    print(f"  Line: {r['line'][:100]}")
