import glob, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

used_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        m = re.search(r'/(?:p|reel|reels)/([A-Za-z0-9_-]+)', u)
        if m:
            used_codes.add(m.group(1))

brain_dir = 'C:/Users/User/.gemini/antigravity/brain'
files = glob.glob(brain_dir + '/**/*.jsonl', recursive=True)

print(f"Searching {len(files)} transcript files...")

found_reels = {}

for fp in files:
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'instagram.com/' in line and ('1M' in line or '1.' in line or '2.' in line or '3.' in line or 'میلیون' in line or 'likes' in line):
                    matches = re.findall(r'instagram\.com/(?:reel|reels|p)/([A-Za-z0-9_-]+)', line)
                    for code in matches:
                        if code not in used_codes and code not in found_reels:
                            found_reels[code] = fp
    except Exception:
        pass

print(f"Total unique unused reel codes found: {len(found_reels)}")
for c, p in list(found_reels.items())[:30]:
    print(f"- {c} in {os.path.basename(os.path.dirname(os.path.dirname(p)))}")
