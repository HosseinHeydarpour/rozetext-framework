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

with open('scratch/test_pool.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Find dicts in test_pool.py
# Let's inspect test_pool by running python on it
import subprocess
res = subprocess.run(['python', '-c', """
import json, sys, re
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

try:
    import scratch.test_pool as tp
    pool = getattr(tp, 'pool', []) + getattr(tp, 'verified_additional', [])
    print(f'Total items in test_pool: {len(pool)}')
    for it in pool:
        u = it.get('source_url', '')
        c = re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', u)
        if not c: continue
        code = c[0]
        v = it.get('source_views', '')
        raw = it.get('extracted_raw_text', '') or it.get('content', '')
        lines = [l.strip() for l in raw.split('\\n') if l.strip()]
        dup = engine.check_duplicate_against_history(raw, raw)
        is_million = ('M' in str(v) or 'm' in str(v) or 'میلیون' in str(v) or '1,' in str(v) or '2,' in str(v) or '3,' in str(v))
        if code.lower() not in db_codes and not dup['is_duplicate'] and is_million and 7 <= len(lines) <= 16:
            print(f'MATCH: [{v}] {code} ({it.get(\"source_page\")}) -> Sim={dup[\"similarity_score\"]}% | lines={len(lines)} | {it.get(\"title\")[:35]}')
except Exception as e:
    print('Import error:', e)
"""], capture_output=True, text=True, encoding='utf-8')

print(res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)
