import os, sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print(f"Length of batch_02: {len(text)}")
# Find all URLs and views
matches = re.findall(r'(https?://[^\s\n]+).*?(?=\n\n|\Z)', text, re.DOTALL)
print(f"Found {len(matches)} URL sections")
for m in matches[:15]:
    print(m[:300])
    print("=" * 40)
