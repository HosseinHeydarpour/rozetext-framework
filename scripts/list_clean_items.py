import sys
import re
from audit_fresh_vs_history import items, get_ngrams

sys.stdout.reconfigure(encoding='utf-8')

with open('published-content-history.md', encoding='utf-8') as f:
    text = f.read()

parts = re.split(r'###\s+Reel\s+#234', text)
baseline_233 = parts[0]
baseline_4grams = set()
for p in baseline_233.split('\n\n'):
    if len(p.strip()) > 30:
        baseline_4grams.update(get_ngrams(p, 4))

print('=== ITEMS WITH SIMILARITY < 20% AGAINST BASELINE 233 ===')
count = 0
for idx, item in enumerate(items):
    txt = item['content']
    ng = get_ngrams(txt, 4)
    comm = ng.intersection(baseline_4grams)
    sim = (len(comm)/len(ng))*100 if ng else 0
    if sim < 20.0:
        count += 1
        print(f"{count}. Idx {idx+1}: {item['title']} ({item['source_page']}) -> Sim: {sim:.1f}%")

print(f"\nTotal clean items: {count}")
