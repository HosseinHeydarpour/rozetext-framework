import os
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load published-content-history.md
with open('published-content-history.md', encoding='utf-8') as f:
    history_text = f.read()

# Tokenizer for 4-grams
def get_ngrams(text, n=4):
    words = re.findall(r'[\w\u0600-\u06FF]+', text)
    if len(words) < n:
        return set()
    return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))

# Extract all paragraphs/reels from history
history_paragraphs = [p.strip() for p in history_text.split('\n\n') if len(p.strip()) > 30]
history_4grams = set()
for p in history_paragraphs:
    history_4grams.update(get_ngrams(p, 4))

print(f"Total history 4-grams indexed: {len(history_4grams)}")

def check_anti_duplication(candidate_text):
    cand_ngrams = get_ngrams(candidate_text, 4)
    if not cand_ngrams:
        return 0, []
    common = cand_ngrams.intersection(history_4grams)
    similarity = (len(common) / len(cand_ngrams)) * 100
    return similarity, list(common)

# Test function
print("Checker ready.")
