import os, glob, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

already_selected = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DZSr1vMN1mr', 'DPjI0mTCIPs', 
    'DKm6Qn6I9vQ', 'DPRj9ddCF5T', 'DbyY0F7tmAn', 'Dd9GQ7HsdZM', 'DdEeNFfs5V3'
}

# Search all files under brain
all_files = glob.glob(r'C:\Users\User\.gemini\antigravity\brain\**\*', recursive=True)
print(f"Total files in brain: {len(all_files)}")

found_reels = []

for fp in all_files:
    if os.path.isdir(fp):
        continue
    # skip binary or massive files
    if not (fp.endswith('.json') or fp.endswith('.md') or fp.endswith('.jsonl') or fp.endswith('.txt')):
        continue
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        continue
        
    # Search for reel links
    for m in re.finditer(r'(?:instagram\.com/reel/|reel/)([A-Za-z0-9_-]{10,12})', content):
        sc = m.group(1)
        if sc in db_codes or sc in already_selected:
            continue
            
        start = max(0, m.start() - 500)
        end = min(len(content), m.end() + 1500)
        snippet = content[start:end]
        
        # Check views 1M+
        v_match = re.search(r'(?:[1-9]\d*[\.,]\d*M|[1-9]\d*M|[۱-۹]\d*[\.,\u066b][۰-۹]*\s*میلیون|[۱-۹]\d*\s*میلیون|\b[1-9]\d{6,}\b\s*(?:ویو|بازدید|views|plays))', snippet)
        if not v_match:
            continue
            
        # Check for Persian text block with at least 5 lines
        persian_lines = []
        for line in snippet.splitlines():
            line_str = line.strip()
            # Check if line has Persian letters and is reasonable length
            if re.search(r'[\u0600-\u06FF]', line_str) and len(line_str) > 10 and not any(tag in line_str for tag in ['#', 'http', 'ویو', 'لایک', 'کامنت', 'آمار', 'اشتراک', 'تحلیل', 'امتیاز']):
                persian_lines.append(line_str)
                
        if len(persian_lines) >= 7:
            txt = '\n'.join(persian_lines[:16])
            found_reels.append((sc, v_match.group(0), txt, fp))

print(f"Found {len(found_reels)} potential candidates across all files!")

# Deduplicate by sc
seen_sc = set()
unique_cands = []
for sc, v, txt, fp in found_reels:
    if sc not in seen_sc:
        seen_sc.add(sc)
        unique_cands.append((sc, v, txt, fp))

print(f"Unique candidates: {len(unique_cands)}")
for sc, v, txt, fp in unique_cands[:20]:
    lines = [l for l in txt.splitlines() if l.strip()]
    print(f"[{sc}] Views: {v} | Lines: {len(lines)} | File: {os.path.basename(fp)}")
    print(f"  Hook: {lines[0] if lines else ''}")
