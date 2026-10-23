import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

scripts = db.get('scripts', [])
print('Total scripts in DB:', len(scripts))

today = [s for s in scripts if s.get('scheduled_date') == '2026-10-18']
print('Scripts for 2026-10-18:', len(today))
for s in sorted(today, key=lambda x: x.get('scheduled_slot', 0)):
    print(f"Slot {s.get('scheduled_slot')}: id={s.get('id')} | title={s.get('title')} | arch={s.get('archetype')} | score={s.get('score')} | url={s.get('source_url')}")

# Check upcoming dates
dates = sorted(list(set(s.get('scheduled_date') for s in scripts if s.get('scheduled_date') and s.get('scheduled_date') >= '2026-10-18')))
print('Upcoming dates in DB:', dates)
for d in dates:
    cnt = len([s for s in scripts if s.get('scheduled_date') == d])
    print(f"  {d}: {cnt} scripts")
