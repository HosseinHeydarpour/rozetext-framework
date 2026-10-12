import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\new_top_50_reels.json"
raw = json.load(open(p, encoding='utf-8'))

# Split by numbered items like "\n1. پیج", "\n2. پیج", etc.
pattern = r'(?:\n|^)(?:\d+\.\s*پیج\s+([^\n]+))'
splits = list(re.finditer(pattern, raw))
print(f"Found {len(splits)} reel items")

for i, m in enumerate(splits):
    start = m.start()
    end = splits[i+1].start() if i+1 < len(splits) else len(raw)
    chunk = raw[start:end]
    page = m.group(1).strip()
    
    # URL
    url_m = re.search(r'https://www\.instagram\.com/reel/([A-Za-z0-9_-]+)/', chunk)
    code = url_m.group(1) if url_m else ''
    
    # Views
    views_m = re.search(r'(?:آمار|ویو|بازدید)[^\n]*', chunk)
    views = views_m.group(0) if views_m else ''
    
    # Text block
    text_m = re.search(r'```(?:text)?\n(.*?)```', chunk, re.DOTALL)
    text = text_m.group(1).strip() if text_m else ''
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    print(f"[{i+1}] {code} | {page} | {views[:40]} | Lines: {len(lines)}")
