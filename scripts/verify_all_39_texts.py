import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

target_scripts = []
for s in db['scripts']:
    d = s.get('scheduled_date')
    slot = s.get('scheduled_slot')
    if d == '2026-10-18' and slot in [4, 5, 6]:
        target_scripts.append(s)
    elif d and d >= '2026-10-19' and d <= '2026-10-24':
        target_scripts.append(s)

print(f"Total target scripts to verify: {len(target_scripts)}")
for i, s in enumerate(target_scripts):
    c = s.get('content', '')
    e = s.get('extracted_raw_text', '')
    lines = [l.strip() for l in c.split('\n') if l.strip()]
    same = (c.strip() == e.strip())
    print(f"#{i+1}: [{s.get('scheduled_date')} Slot {s.get('scheduled_slot')}] {s.get('source_page')} ({s.get('source_views')}) | Lines: {len(lines)} | Match raw: {same} | Title: {s.get('title')[:30]}")
    if not same:
        print(f"  DIFF DETECTED in #{i+1}!")
