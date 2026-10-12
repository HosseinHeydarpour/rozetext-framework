import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")

with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

scripts = db.get("scripts", [])
print(f"Total scripts in DB: {len(scripts)}")

urls = set()
for s in scripts:
    u = s.get("source_url")
    if u:
        code = u.strip().rstrip("/").split("/")[-1]
        urls.add(code)

print(f"Unique reel shortcodes in DB: {len(urls)}")

# Check dates and unpublished
unpub = [s for s in scripts if not s.get("published", False)]
print(f"Unpublished count: {len(unpub)}")
by_date = {}
for s in unpub:
    d = s.get("scheduled_date", "NoDate")
    by_date.setdefault(d, []).append(s)

for d in sorted(by_date.keys()):
    print(f"\nDate {d} ({len(by_date[d])} scripts):")
    for s in by_date[d]:
        c = s.get("extracted_raw_text") or s.get("content") or ""
        hook = c.splitlines()[0] if c.splitlines() else "EMPTY"
        print(f"  Slot {s.get('scheduled_slot')}: [{s.get('id')}] {s.get('source_page')} | Views: {s.get('source_views')} | Hook: {hook[:40]}")
