import os, glob, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

# 9 already selected codes
already_selected = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DZSr1vMN1mr', 'DPjI0mTCIPs', 
    'DKm6Qn6I9vQ', 'DPRj9ddCF5T', 'DbyY0F7tmAn', 'Dd9GQ7HsdZM', 'DdEeNFfs5V3'
}

print(f"Already selected: {len(already_selected)} reels")

# Let's search all md and json files in brain folders
brain_files = glob.glob(r'C:\Users\User\.gemini\antigravity\brain\**\*.*', recursive=True)
candidate_files = [f for f in brain_files if f.endswith('.json') or f.endswith('.md')]

print(f"Total brain files to search: {len(candidate_files)}")

found_reels = {}

for fpath in candidate_files:
    if 'transcript' in fpath or 'history' in fpath:
        continue
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        continue
        
    # Search for reels with 1M+ or ویو or shortcodes
    # Look for instagram.com/reel/([A-Za-z0-9_-]+)
    matches = re.finditer(r'instagram\.com/reel/([A-Za-z0-9_-]+)', content)
    for m in matches:
        sc = m.group(1)
        if sc in db_codes or sc in already_selected:
            continue
        if sc not in found_reels:
            # Check context around match for views
            start = max(0, m.start() - 300)
            end = min(len(content), m.end() + 1000)
            context = content[start:end]
            
            # Check if views 1M+ is mentioned
            is_1m = bool(re.search(r'(?:[1-9]\d*[\.,]\d*M|[1-9]\d*M|[۱-۹]\d*[\.,\u066b][۰-۹]*\s*میلیون|[۱-۹]\d*\s*میلیون|\b[1-9]\d{6,}\b)', context))
            if is_1m:
                found_reels[sc] = {
                    'code': sc,
                    'file': fpath,
                    'context': context
                }

print(f"Found {len(found_reels)} candidate shortcodes with 1M+ in brain files!")
for sc, info in list(found_reels.items())[:20]:
    print(f"[{sc}] in {os.path.basename(info['file'])}")
