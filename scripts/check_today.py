import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

print('=== TODAY (2026-10-06) SCRIPTS ===')
today_scripts = [s for s in db.get('scripts', []) if s.get('scheduled_date') == '2026-10-06']
print(f"Total scripts for 2026-10-06: {len(today_scripts)}")
for s in sorted(today_scripts, key=lambda x: x.get('scheduled_slot', 0)):
    print(f"Slot {s.get('scheduled_slot')}: published={s.get('published')} | ID: {s.get('id')} | Score: {s.get('score')}")
    print(f"  Title: {s.get('title')}")
    print(f"  Arch: {s.get('archetype')}")
    print(f"  Time: {s.get('recommended_time')} | Source: {s.get('source_page')} ({s.get('source_views')}) | URL: {s.get('source_url')}")
print('\n=== ALL UNPUBLISHED IN ENTIRE DB ===')
unpub = [s for s in db.get('scripts', []) if not s.get('published')]
print(f"Total unpublished: {len(unpub)}")
for s in unpub:
    print(f"[{s.get('scheduled_date')} - Slot {s.get('scheduled_slot')} @ {s.get('recommended_time')}] Score: {s.get('score')} | {s.get('title')} | ID: {s.get('id')}")
