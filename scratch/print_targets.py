import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt', 'r', encoding='utf-8') as f:
    batch_01_text = f.read()

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8') as f:
    top_50_text = f.read()

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    hunted_42 = json.load(f)

targets = [
    'C5WPI8OCK4x',
    'DZDRxCkNgjw',
    'DNTYt15oqYj',
    'DZSr1vMN1mr',
    'DPjI0mTCIPs',
    'DKm6Qn6I9vQ',
    'DQHm9z6CMeL',
    'DHy7292o-GE',
    'DSODhFciOYd',
    'DdcmkgQuMXn',
    'DIKL9gZqM6_',
    'DIRfksnIzoB',
    'DUdr6AqDEPn'
]

for t in targets:
    print(f"\n==================== CODE: {t} ====================")
    # Check hunted_42
    m_hunted = [x for x in hunted_42 if t in x.get('source_url', '')]
    if m_hunted:
        it = m_hunted[0]
        print(f"SOURCE: hunted-42 | Page: {it.get('source_page')} | Views: {it.get('source_views')}")
        print("TEXT:")
        print(it.get('extracted_raw_text') or it.get('content'))
        continue
    
    # Check top_50_text
    pos = top_50_text.find(t)
    if pos != -1:
        start = max(0, pos - 200)
        end = min(len(top_50_text), pos + 1000)
        snippet = top_50_text[start:end]
        print(f"SOURCE: top_50_viral_delneveshte_reels.txt")
        print(snippet[:600])
        continue

    # Check batch_01_text
    pos = batch_01_text.find(t)
    if pos != -1:
        start = max(0, pos - 200)
        end = min(len(batch_01_text), pos + 1000)
        snippet = batch_01_text[start:end]
        print(f"SOURCE: batch_01.txt")
        print(snippet[:600])
        continue
