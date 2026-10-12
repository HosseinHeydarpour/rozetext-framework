import os
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

codes = ["DJeyrN9oAxI", "DMVWoiaor6o", "DFK4s89or6Z", "DKm6Qn6I9VQ"]
base = r"C:\Users\User\.gemini\antigravity\brain"

found = {}

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(('.json', '.jsonl', '.py', '.txt', '.md')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
            except Exception:
                continue
                
            for c in codes:
                if c in content:
                    # Look for content or extracted_raw_text or multi-line quotes
                    idx = 0
                    while True:
                        idx = content.find(c, idx)
                        if idx == -1:
                            break
                        # window
                        win = content[max(0, idx-1000):min(len(content), idx+2500)]
                        if "content" in win or "extracted_raw_text" in win:
                            found.setdefault(c, []).append((os.path.basename(path), win))
                            break
                        idx += len(c)

print(f"Results for target codes: {list(found.keys())}")
for c, list_wins in found.items():
    print(f"\n==================== CODE: {c} ({len(list_wins)} matches) ====================")
    for fname, win in list_wins[:2]:
        print(f"File: {fname}")
        print(win[:800])
