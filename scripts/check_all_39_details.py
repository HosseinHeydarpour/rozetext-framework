import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Collect Sunday slots 4,5,6 and Mon-Sat
scripts_to_check = []
for s in db['scripts']:
    d = s.get('scheduled_date')
    slot = s.get('scheduled_slot')
    if d == '2026-10-18' and slot in [4, 5, 6]:
        scripts_to_check.append(s)
    elif d and '2026-10-19' <= d <= '2026-10-24':
        scripts_to_check.append(s)

# Sort by date and slot
scripts_to_check.sort(key=lambda x: (x.get('scheduled_date', ''), x.get('scheduled_slot', 0)))

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
end = int(sys.argv[2]) if len(sys.argv) > 2 else len(scripts_to_check)

for i in range(start, min(end, len(scripts_to_check))):
    sc = scripts_to_check[i]
    print(f"=== #{i+1:02d}: [{sc['scheduled_date']} Slot {sc['scheduled_slot']}] {sc.get('source_page')} ({sc.get('source_views')}) ===")
    print(f"URL: {sc.get('source_url')}")
    print(f"Title: {sc.get('title')}")
    lines = [l.strip() for l in sc.get('content', '').splitlines() if l.strip()]
    print(f"Lines count: {len(lines)}")
    print("Text:")
    for line in lines:
        print(f"  | {line}")
    print()
