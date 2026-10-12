import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

p_full = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c)

found_scripts = {}

with open(p_full, 'r', encoding='utf-8', errors='ignore') as f:
    for line_idx, line in enumerate(f):
        if 'source_url' not in line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        
        content = ""
        if isinstance(row.get('content'), str):
            content = row['content']
        elif isinstance(row.get('tool_calls'), list):
            content = json.dumps(row['tool_calls'], ensure_ascii=False)
        elif isinstance(row.get('thinking'), str):
            content = row['thinking']
            
        # Look for JSON arrays or objects in content
        # Or search for patterns like "source_url": "...", "extracted_raw_text": "..."
        for chunk in re.findall(r'\{[^{}]+"source_url"[^{}]+\}', content):
            try:
                obj = json.loads(chunk)
                u = obj.get('source_url', '')
                m = re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', u)
                if m:
                    code = m[0]
                    if code not in db_codes and obj.get('extracted_raw_text'):
                        found_scripts[code] = obj
            except Exception:
                pass

        # Also search for python list of dicts or larger json structures
        matches = re.finditer(r'\{\s*"title"\s*:\s*"[^"]+".*?"source_url"\s*:\s*"https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?".*?\}', content, re.DOTALL)
        for m in matches:
            code = m.group(1)
            if code not in db_codes and code not in found_scripts:
                try:
                    obj = json.loads(m.group(0))
                    if obj.get('extracted_raw_text'):
                        found_scripts[code] = obj
                except Exception:
                    pass

print(f"Extracted {len(found_scripts)} complete script objects from transcript_full.jsonl")
for code, obj in list(found_scripts.items())[:20]:
    v = obj.get('source_views', '')
    p = obj.get('source_page', '')
    t = obj.get('title', '')
    print(f"[{v}] {code} ({p}) -> {t[:40]}")
