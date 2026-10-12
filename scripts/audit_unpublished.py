import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

unpub = [s for s in db.get('scripts', []) if not s.get('published')]
print(f"Total unpublished scripts: {len(unpub)}\n")

for s in unpub:
    print(f"=== [{s.get('scheduled_date')} - Slot {s.get('scheduled_slot')}] {s.get('title')} ===")
    print(f"ID: {s.get('id')} | Arch: {s.get('archetype')} | Score: {s.get('score')}")
    print(f"Source: {s.get('source_page')} ({s.get('source_views')}) | URL: {s.get('source_url')}")
    print(f"Content:\n{s.get('content')}")
    print(f"Caption:\n{s.get('caption')}")
    print("-" * 60)
