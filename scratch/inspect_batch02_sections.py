import os, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's inspect sections
sections = re.split(r'\n(?=### |\d+\. |https://)', text)
for i, s in enumerate(sections):
    if 'https://' in s:
        print(f"=== ENTRY {i} ===")
        print(s[:500])
        print("=" * 40)
