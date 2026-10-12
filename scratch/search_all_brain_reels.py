import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load existing DB codes
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_codes = set()
for s in db.get('scripts', []):
    for fld in [s.get('source_url', ''), s.get('extra_notes', '')]:
        for c in re.findall(r'reel[s]?/([A-Za-z0-9_-]+)', fld):
            db_codes.add(c)

print(f"Existing DB codes to exclude: {len(db_codes)}")

# 2. Search across ALL brain transcripts for extracted scripts
base = r'C:\Users\User\.gemini\antigravity\brain'
transcript_files = []
for root, dirs, fnames in os.walk(base):
    for f in fnames:
        if f in ['transcript_full.jsonl', 'transcript.jsonl']:
            transcript_files.append(os.path.join(root, f))

print(f"Found {len(transcript_files)} transcript files across brain.")

candidates = {}

for tf in transcript_files:
    try:
        with open(tf, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'instagram.com/reel' not in line or 'extracted_raw_text' not in line:
                    continue
                # Find all JSON blocks in line
                # Look for {"title": ..., "source_url": ..., "extracted_raw_text": ...}
                # Use regex to find script objects
                # or find keys
                matches = re.finditer(r'\{[^{}]*"source_url"\s*:\s*"https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?"[^{}]*\}', line)
                for m in matches:
                    code = m.group(1)
                    if code in db_codes or code in candidates:
                        continue
                    try:
                        obj = json.loads(m.group(0))
                        if obj.get('extracted_raw_text') and len(obj['extracted_raw_text'].split('\n')) >= 5:
                            candidates[code] = obj
                    except Exception:
                        pass
    except Exception:
        pass

print(f"Found {len(candidates)} raw JSON objects.")

# Also search for markdown structured entries like:
# ### X. ریلز ...
# - **آدرس ریلز (`source_url`):** ...
# - **متن دقیق ... (`extracted_raw_text`):**
md_candidates = {}
for tf in transcript_files:
    try:
        with open(tf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # find blocks with reel url and extracted text
            blocks = re.split(r'###\s+\d+\.\s+ریلز|\n---\n', content)
            for b in blocks:
                if 'instagram.com/reel' not in b:
                    continue
                m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
                if not m_url:
                    continue
                code = m_url.group(1)
                if code in db_codes or code in md_candidates or code in candidates:
                    continue
                
                # Check views
                m_views = re.search(r'\*\*بازدید.*?\:\*\*\s*([^\n\r]+)', b)
                # Check page
                m_page = re.search(r'\*\*آیدی.*?\:\*\*\s*([^\n\r]+)', b)
                # Check text block
                m_text = re.search(r'```(?:text)?\s*([\s\S]*?)```', b)
                # Check title or archetype
                m_arch = re.search(r'\*\*آرکتایپ.*?\:\*\*\s*([^\n\r]+)', b)
                
                if m_text and m_views:
                    raw_text = m_text.group(1).strip()
                    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                    if len(lines) >= 6:
                        md_candidates[code] = {
                            'code': code,
                            'url': m_url.group(0),
                            'views': m_views.group(1).strip(),
                            'page': m_page.group(1).strip() if m_page else '@unknown',
                            'archetype': m_arch.group(1).strip() if m_arch else 'آرکتایپ ۱',
                            'text': raw_text,
                            'lines_count': len(lines)
                        }
    except Exception:
        pass

print(f"Found {len(md_candidates)} markdown structured candidates.")
all_valid = {**candidates, **md_candidates}
print(f"Total unique fresh candidates: {len(all_valid)}")

for code, item in list(md_candidates.items())[:25]:
    print(f"[{item['views']}] {code} ({item['page']}) -> lines={item['lines_count']} | Hook: {item['text'].split(chr(10))[0][:40]}")
