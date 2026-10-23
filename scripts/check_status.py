import json
import os
import glob

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

scripts = db.get('scripts', [])
print(f"Total in DB: {len(scripts)}")
sun = [i for i in scripts if i.get('scheduled_date') == '2026-10-18']
print(f"Sunday items: {len(sun)}")
for s in sun:
    print(f"  Slot {s.get('slot')}: {s.get('id')} - {s.get('title')}")

frames = glob.glob('downloads/frames/*.jpg') + glob.glob('downloads/frames/*.png')
print(f"\nTotal frames in downloads/frames/: {len(frames)}")
for fr in frames[-15:]:
    print(" ", fr)
