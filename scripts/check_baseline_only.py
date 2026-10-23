import re
import sys
from audit_fresh_vs_history import get_ngrams, items

sys.stdout.reconfigure(encoding='utf-8')

with open('published-content-history.md', encoding='utf-8') as f:
    text = f.read()

parts = re.split(r'###\s+Reel\s+#234', text)
baseline_233 = parts[0]
later_part = '### Reel #234' + parts[1] if len(parts) > 1 else ''

baseline_4grams = set()
for p in baseline_233.split('\n\n'):
    if len(p.strip()) > 30:
        baseline_4grams.update(get_ngrams(p, 4))

print(f'Baseline 233 4-grams: {len(baseline_4grams)}')

flagged_baseline = []
for idx, item in enumerate(items):
    c_text = item['content']
    cand_ngrams = get_ngrams(c_text, 4)
    common_baseline = cand_ngrams.intersection(baseline_4grams)
    sim_baseline = (len(common_baseline) / len(cand_ngrams)) * 100 if cand_ngrams else 0
    if sim_baseline > 10.0 or len(common_baseline) >= 3:
        flagged_baseline.append((idx, item['title'], sim_baseline, len(common_baseline)))

print(f"Total flagged against baseline 233: {len(flagged_baseline)}")
for idx, title, sim, count in flagged_baseline:
    print(f"Item {idx+1}: {title} -> {sim:.1f}% ({count} ngrams)")
