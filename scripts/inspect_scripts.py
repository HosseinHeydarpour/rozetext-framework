import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

scripts = db.get('scripts', [])
print(f"Total scripts in db: {len(scripts)}")

by_date = {}
for s in scripts:
    d = s.get('scheduled_date', 'unknown')
    by_date.setdefault(d, []).append(s)

for d in sorted(by_date.keys()):
    print(f"\n=== Date: {d} ({len(by_date[d])} scripts) ===")
    for s in sorted(by_date[d], key=lambda x: x.get('scheduled_slot', 0)):
        pub = "PUBLISHED" if s.get('published') else "UNPUBLISHED"
        print(f"  Slot {s.get('scheduled_slot')}: [{pub}] {s.get('recommended_time')} | Arch: {s.get('archetype', '')[:15]} | Score: {s.get('score')} | {s.get('title')} | ID: {s.get('id')}")

print("\n=== All UNPUBLISHED SCRIPTS ===")
unpub = [s for s in scripts if not s.get('published')]
print(f"Total unpublished: {len(unpub)}")
for s in unpub:
    print(f"- Date: {s.get('scheduled_date')} | Slot: {s.get('scheduled_slot')} | Time: {s.get('recommended_time')} | Arch: {s.get('archetype')} | Score: {s.get('score')}")
    print(f"  Title: {s.get('title')}")
    print(f"  Source: {s.get('source_page')} ({s.get('source_views')}) - URL: {s.get('source_url')}")
    print(f"  Content:\n{s.get('content')}")
    print("-" * 50)
