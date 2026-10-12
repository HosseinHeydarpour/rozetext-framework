import glob, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Collect existing db texts & used urls/codes
used_codes = set()
existing_db_texts = []
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append(txt.strip())

files = [
    r'D:\rozetext content\top_50_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt',
    r'D:\rozetext content\top_15_viral_delneveshte_reels.txt'
]

print("Scanning files in D:\\rozetext content...")

# Let's inspect how reels are formatted in these files
for fp in files:
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    print(f"File: {os.path.basename(fp)} ({len(text)} chars)")
    # Show first 500 chars to understand format
    print(text[:300])
    print("-" * 50)
