import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/scripts-db.json.bak_pre_42_import", "r", encoding="utf-8") as f:
    db = json.load(f)

scripts = db.get("scripts", [])
print(f"Total scripts in DB backup: {len(scripts)}")
pub = [s for s in scripts if s.get("published")]
print(f"Published scripts count: {len(pub)}")
for s in scripts:
    print(f"[{s.get('scheduled_date')} | Slot #{s.get('scheduled_slot')}] Pub: {s.get('published')} | Reel #{s.get('history_reel_number')} | {s.get('title', '')[:45]}")
