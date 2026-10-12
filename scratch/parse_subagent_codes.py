import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

used_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))

print(f"Total used codes in scripts-db: {len(used_codes)}")

found_in_subagent = {}

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        matches = re.findall(r'instagram\.com/(?:reel|reels|p)/([A-Za-z0-9_-]+)', line)
        for code in set(matches):
            if code not in used_codes:
                found_in_subagent.setdefault(code, []).append(idx)

print(f"Total unused codes in subagent: {len(found_in_subagent)}")
for c, steps in found_in_subagent.items():
    print(f"- {c}: steps {steps}")
