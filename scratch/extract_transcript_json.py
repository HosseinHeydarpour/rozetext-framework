import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

# Find all blocks in transcript that have reels with verbatim text
print("Scanning transcript for scripts and reels...")

extracted_items = []

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        # Check if line contains json-like script structures or reel blocks
        if 'source_url' in line and 'extracted_raw_text' in line:
            # try finding json objects
            matches = re.findall(r'(\{"title":\s*"[^"]+",[\s\S]*?"source_url":\s*"https://www\.instagram\.com/reel/[^"]+"[\s\S]*?\})', line)
            for m in matches:
                try:
                    obj = json.loads(m)
                    extracted_items.append(obj)
                except:
                    pass

print(f"Total structured JSON items found in transcript: {len(extracted_items)}")

# Check each item
valid = []
seen = set()
for it in extracted_items:
    u = it.get('source_url', '').strip()
    if not u or u in seen or u in db_urls:
        continue
    seen.add(u)
    
    txt = it.get('extracted_raw_text') or it.get('content') or ""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    if not (7 <= len(lines) <= 16):
        continue
        
    views_str = str(it.get('source_views', ''))
    # check million
    is_m = False
    if 'میلیون' in views_str or 'M' in views_str or 'm' in views_str:
        is_m = True
    else:
        digs = re.findall(r'[\d,٬]{7,}', views_str)
        if digs:
            is_m = True
    if not is_m:
        continue
        
    dup = engine.check_duplicate_against_history(txt, txt)
    if dup['is_duplicate']:
        continue
        
    valid.append({
        'url': u,
        'title': it.get('title'),
        'page': it.get('source_page'),
        'views': views_str,
        'lines': len(lines),
        'sim': dup['similarity_score'],
        'hook': lines[0] if lines else '',
        'item': it
    })

print(f"Valid candidates from transcript: {len(valid)}")
for v in valid:
    print(f"- [{v['views']}] {v['page']} | L:{v['lines']} | Sim:{v['sim']:.1f}% | {v['url']}")
    print(f"   Hook: {v['hook']}")
