import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        db_urls.add(u.strip().rstrip('/').split('/')[-1])
    n = s.get('extra_notes', '')
    for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', n):
        db_urls.add(c)

test_codes = ['DbyY0F7tmAn', 'DbbPmLFNZbj', 'DPeaox9CPJk', 'DPRj9ddCF5T', 'DO_homTiPTp']

print("=== CHECKING REELS FROM STEP 276 ===")
for c in test_codes:
    in_db = c in db_urls
    print(f"Code: {c} | inDB: {in_db}")
