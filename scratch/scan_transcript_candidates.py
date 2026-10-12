import json
import re
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

print(f"DB currently has {len(db_codes)} codes.")

all_blocks = []

with open(p_full, 'r', encoding='utf-8', errors='ignore') as f:
    for line_idx, line in enumerate(f):
        if 'instagram.com/reel' not in line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        
        # gather all text in this row
        texts = []
        if isinstance(row.get('content'), str):
            texts.append(row['content'])
        if isinstance(row.get('thinking'), str):
            texts.append(row['thinking'])
        if isinstance(row.get('tool_calls'), list):
            for tc in row['tool_calls']:
                args = tc.get('args', {})
                for v in args.values():
                    if isinstance(v, str):
                        texts.append(v)
        
        row_text = "\n".join(texts)
        if 'instagram.com/reel' in row_text:
            all_blocks.append((line_idx, row_text))

print(f"Found {len(all_blocks)} rows with reel links.")

# Search for sections with reel links and code blocks or text
results = {}
for line_idx, text in all_blocks:
    # Split text into sections by markdown headers or dividers
    parts = re.split(r'###|\n---\n|================', text)
    for part in parts:
        urls = re.findall(r'instagram\.com/reel[s]?/([A-Za-z0-9_-]+)', part)
        if not urls:
            continue
        code = urls[0]
        if code in db_codes or len(code) < 5 or code in ['TEST99', 'VIRAL']:
            continue
        
        # check views
        m_views = re.search(r'(\d+[\.,]?\d*\s*[Mm]|\d+,\d+,\d+\s*بازدید|\d+[\.,]?\d*\s*میلیون)', part)
        # check on-screen text
        m_text = re.search(r'```(?:text)?\s*([\s\S]*?)```', part)
        raw_text = m_text.group(1).strip() if m_text else ""
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        
        if code not in results or (not results[code]['text'] and raw_text):
            results[code] = {
                'code': code,
                'views': m_views.group(1) if m_views else (results.get(code, {}).get('views', 'Unknown')),
                'text': raw_text,
                'lines': len(lines),
                'part': part[:300]
            }

valid_fresh = [r for r in results.values() if r['lines'] >= 6 and ('M' in str(r['views']) or 'میلیون' in str(r['views']) or any(k in str(r['views']) for k in ['1,', '2,', '3,', '4,', '5,']))]
print(f"Found {len(valid_fresh)} valid fresh reels:")
for r in valid_fresh:
    print(f"[{r['views']}] {r['code']} ({r['lines']} lines): {r['text'].split(chr(10))[0]}")
