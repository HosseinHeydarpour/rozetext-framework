import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

seen_codes = set()
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        seen_codes.add(u.strip().rstrip('/').split('/')[-1])

print(f"DB codes count: {len(seen_codes)}")

found_reels = []

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 'vahidrezakhoshbayan/reel' in line or 'heliumm.__/reel' in line or '___yeharf/reel' in line or 'instagram.com/reel/' in line:
            # find all reel codes
            codes = set(re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', line))
            for c in codes:
                if c in seen_codes:
                    continue
                # check views near c
                pos = line.find(c)
                snippet = line[max(0, pos-200):min(len(line), pos+500)]
                m_view = re.search(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', snippet)
                if m_view and '0.' not in m_view.group(1):
                    found_reels.append((c, m_view.group(1), idx, snippet))

print(f"Total candidate mentions found: {len(found_reels)}")
unique_c = {}
for c, v, idx, snip in found_reels:
    if c not in unique_c:
        unique_c[c] = (v, idx, snip)

print(f"Unique unused codes: {len(unique_c)}")
for c, (v, idx, snip) in list(unique_c.items())[:30]:
    print(f"- {c} | {v} | line {idx}")
