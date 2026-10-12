import sys, os, json, re
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('./scratch'))
sys.stdout.reconfigure(encoding='utf-8')
from server import PublisherEngine

engine = PublisherEngine()

import step1073_code

all_reels = step1073_code.day5_reels + step1073_code.day6_reels + step1073_code.day7_reels
print(f'Total reels in day5-7: {len(all_reels)}')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

for idx, r in enumerate(all_reels):
    u = r.get('source_url', '').strip()
    txt = r.get('content', '')
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    views = r.get('source_views', '')
    dup = engine.check_duplicate_against_history(txt, txt)
    in_db = u in db_urls
    print(f'#{idx+1} [{views}] {r.get("source_page")} | L:{len(lines)} | inDB:{in_db} | dup:{dup["is_duplicate"]} ({dup["similarity_score"]:.1f}%) | {u}')
    print(f'   Hook: {lines[0] if lines else ""}')
