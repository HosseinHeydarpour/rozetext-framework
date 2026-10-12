import sys, os
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8') as f:
    text = f.read()

b = text.find('DdcmkgQuMXn')
print(text[b-100:b+1500])
