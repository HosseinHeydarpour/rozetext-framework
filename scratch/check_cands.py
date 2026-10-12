import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
scripts = db.get('scripts', [])

urls = [
    'C_tJLJQx_7T',
    'DChXfbBRDFR',
    'DGLp45fI3AI',
    'DF0fjASo1o4',
    'DDXcjgBoIIb',
    'DEfhdKfIJ0N',
    'DCKORIQhLAi',
    'DIhCXgqIMl0',
    'DCCfSjmhVKI',
    'DdcA1OVC3dg',
    'DdPDb35qWnW',
    'Ddmz-WgRM4K'
]

for code in urls:
    matches = [s for s in scripts if code in s.get('source_url', '') or code in s.get('extra_notes', '')]
    if matches:
        m = matches[0]
        print(f"ALREADY IN DB: {code} -> {m.get('scheduled_date')} Slot {m.get('scheduled_slot')}: {m.get('title')}")
    else:
        print(f"FRESH: {code}")
