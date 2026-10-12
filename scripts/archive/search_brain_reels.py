import os
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
from server import ENGINE

base = r'C:\Users\User\.gemini\antigravity\brain'
from test_pool import pool
pool_urls = set(r.get('source_url') for r in pool)

found = []

# Regex to find reel blocks with text and views
pattern = re.compile(r'https?://(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)/?', re.IGNORECASE)

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.md') or f.endswith('.txt') or (f.endswith('.json') and 'scripts-db' not in f):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fp:
                    content = fp.read()
            except Exception:
                continue

            for match in pattern.finditer(content):
                code = match.group(1)
                full_url = f"https://www.instagram.com/reel/{code}/"
                if full_url in pool_urls:
                    continue
                # Look around match for text block and views
                start = max(0, match.start() - 300)
                end = min(len(content), match.end() + 1500)
                window = content[start:end]
                
                # Check for 1M+ views
                has_1m = False
                view_val = ""
                for vm in re.finditer(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', window, re.IGNORECASE):
                    val = vm.group(1)
                    # Exclude 0.x M
                    if '0.' not in val:
                        has_1m = True
                        view_val = val
                        break
                
                if has_1m:
                    # Look for code block ```text ... ``` or quotes
                    t_match = re.search(r'```(?:text)?\s*(.*?)\s*```', window, re.DOTALL)
                    txt = ""
                    if t_match:
                        txt = t_match.group(1).strip()
                    else:
                        # Check lines with Persian
                        pass
                    
                    if txt:
                        lines = [l.strip() for l in txt.splitlines() if l.strip() and not l.startswith('وحیدرضا') and not l.startswith('@')]
                        if 7 <= len(lines) <= 16:
                            dup = ENGINE.check_duplicate_against_history(txt, txt)
                            if not dup['is_duplicate']:
                                found.append((code, view_val, len(lines), lines[0][:40], txt, full_url, path))
                                pool_urls.add(full_url)

print(f'Found {len(found)} candidate reels!')
for c, v, l, h, _, u, p in found:
    print(f'{c} | {v} | {l} lines | {h} | {os.path.basename(p)}')
