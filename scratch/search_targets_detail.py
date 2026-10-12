import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

target_codes = [
    'DG8jFKGIWjY', 'DHMRcwUIAiZ', 'DR7fbNlCBle', 'DcjQOwtN86T',
    'DMf5pj2oQCN', 'DdhsbU4Iw6x', 'DZX3utUt9xI', 'DdcmkgQuMXn',
    'DObgpFniAm-', 'DSp5q5XiOlJ', 'DD9GzMOsZtE', 'DI4PK_6qlED',
    'DdM8l12uV5Z', 'DIb21i1IlXx', 'DHlzMLlI6Ry', 'DJR63KJIy2t'
]

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

print(f"Searching for details on {len(target_codes)} reels...")

results = {}

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line_idx, line in enumerate(f):
        for code in target_codes:
            if code in line and code not in results:
                pos = line.find(code)
                snippet = line[max(0, pos-400):min(len(line), pos+2000)]
                results[code] = (line_idx, snippet)

print(f"Found {len(results)} matches in transcript.")

for code, (line_idx, snip) in results.items():
    print(f"\n====================== CODE: {code} (Line {line_idx}) ======================")
    # Look for views, creator, text
    print(snip[:1200])
