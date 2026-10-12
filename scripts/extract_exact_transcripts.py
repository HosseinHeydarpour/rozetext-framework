import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

path = r"C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\chunks\transcript_full\00000038.jsonl"
with open(path, "r", encoding="utf-8") as f:
    full_text = f.read()

target_codes = ["DJeyrN9oAxI", "DMVWoiaor6o", "DFK4s89or6Z", "DKm6Qn6I9VQ"]

for c in target_codes:
    print(f"\n============================== {c} ==============================")
    # find all occurrences of code
    pos = 0
    while True:
        idx = full_text.find(c, pos)
        if idx == -1:
            break
        # look for json object or dict near idx
        start = max(0, idx - 800)
        end = min(len(full_text), idx + 2500)
        window = full_text[start:end]
        
        # Check if there is "content": or "extracted_raw_text":
        if "extracted_raw_text" in window or "content" in window or "هوک:" in window:
            print("FOUND WINDOW at pos", idx)
            print(window[:1500])
            break
        pos = idx + len(c)
