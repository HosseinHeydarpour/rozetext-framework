import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

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

with open('scratch/subagent_step279.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract json
m = re.search(r'```json\s*([\s\S]*?)```', text)
data = json.loads(m.group(1)) if m else {}

reels = data.get('millionReels', [])
print(f"Total million reels in step 279: {len(reels)}")

unused_million = []
for r in reels:
    rid = r.get('id')
    v = r.get('views')
    in_db = rid in db_urls
    if not in_db:
        unused_million.append((rid, v, r.get('href')))

print(f"\nUnused million reels from vahidrezakhoshbayan: {len(unused_million)}")
for rid, v, href in unused_million:
    print(f"- {rid} | {v} | {href}")
