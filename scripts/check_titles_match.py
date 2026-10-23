import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

scripts_to_check = []
for s in db['scripts']:
    d = s.get('scheduled_date')
    slot = s.get('scheduled_slot')
    if d == '2026-10-18' and slot in [4, 5, 6]:
        scripts_to_check.append(s)
    elif d and '2026-10-19' <= d <= '2026-10-24':
        scripts_to_check.append(s)

scripts_to_check.sort(key=lambda x: (x.get('scheduled_date', ''), x.get('scheduled_slot', 0)))

for i, sc in enumerate(scripts_to_check):
    title = sc.get('title', '')
    lines = [l.strip() for l in sc.get('content', '').splitlines() if l.strip()]
    first_line = lines[0] if lines else ''
    second_line = lines[1] if len(lines) > 1 else ''
    print(f"#{i+1:02d} [{sc['scheduled_date']} S{sc['scheduled_slot']}] Title: {title}")
    print(f"    Line 1: {first_line}")
    print(f"    Line 2: {second_line}")
    print("-" * 50)
