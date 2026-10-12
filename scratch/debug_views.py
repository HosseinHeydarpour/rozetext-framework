import os, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's find all occurrences of "لینک:" and print the stats
entries = re.findall(r'(?:لینک|آمار|متن دقیق).*?(?=\n\n|\Z)', text, re.DOTALL)
lines = text.splitlines()
for i, l in enumerate(lines):
    if 'لینک:' in l or 'آمار:' in l:
        print(l)
    if 'میلیون' in l and 'آمار' in lines[max(0, i-2)]:
        print(f"--> {lines[max(0, i-2)]} | {l}")
