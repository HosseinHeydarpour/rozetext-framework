import json, re

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

used_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))

verified_9 = [
    'C5WPI8OCK4x',
    'DZDRxCkNgjw',
    'DNTYt15oqYj',
    'DZSr1vMN1mr',
    'DPjI0mTCIPs',
    'DKm6Qn6I9vQ',
    'DQHm9z6CMeL',
    'DPRj9ddCF5T',
    'DbyY0F7tmAn'
]

print("Checking 9 verified reels against scripts-db.json:")
for c in verified_9:
    is_used = c in used_codes
    print(f"- {c}: used={is_used}")
