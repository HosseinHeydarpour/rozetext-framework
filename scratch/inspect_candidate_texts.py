import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

codes_to_check = [
    'DHy7292o-GE', 'DSODhFciOYd', 'C_8r9QeuqGO', 'DIKL9gZqM6_', 
    'DIRfksnIzoB', 'DHlzMLlI6Ry', 'DPRj9ddCF5T', 'DIJ0fkOoP5I',
    'DKm6Qn6I9vQ', 'DQHm9z6CMeL', 'DPjI0mTCIPs'
]

files = [
    r'D:\rozetext content\top_50_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt'
]

for code in codes_to_check:
    print(f"\n=================== CODE: {code} ===================")
    found = False
    for fp in files:
        if not os.path.exists(fp):
            continue
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if code in text:
            # find section
            idx = text.find(code)
            start = max(0, idx - 200)
            end = min(len(text), idx + 2000)
            print(f"Found in {os.path.basename(fp)}:")
            print(text[start:end][:1500])
            found = True
            break
    if not found:
        print("Not found in files.")
