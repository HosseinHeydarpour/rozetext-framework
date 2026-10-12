import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt', 'r', encoding='utf-8') as f:
    text = f.read()

codes = ['DHy7292o-GE', 'DSODhFciOYd', 'DIKL9gZqM6_', 'DIRfksnIzoB', 'DUdr6AqDEPn', 'C_8r9QeuqGO']
for c in codes:
    if c in text:
        idx = text.find(c)
        print('=== ' + c + ' ===')
        print(text[max(0, idx-50):min(len(text), idx+800)])
