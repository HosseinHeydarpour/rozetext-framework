import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('published-content-history.md', encoding='utf-8') as f:
    history_text = f.read()

def get_ngrams(text, n=4):
    words = re.findall(r'[\w\u0600-\u06FF]+', text)
    if len(words) < n:
        return set()
    return set(' '.join(words[i:i+n]) for i in range(len(words)-n+1))

history_paragraphs = [p.strip() for p in history_text.split('\n\n') if len(p.strip()) > 30]
history_4grams = set()
for p in history_paragraphs:
    history_4grams.update(get_ngrams(p, 4))

print(f"Total history 4-grams indexed across ALL 319 reels: {len(history_4grams)}")

items = json.load(open('data/hunted-42-fresh-multiaccount-verified.json', encoding='utf-8'))

fresh_items = []
dupe_items = []

for idx, item in enumerate(items):
    c_text = item['content']
    cand_ngrams = get_ngrams(c_text, 4)
    common = cand_ngrams.intersection(history_4grams)
    sim = (len(common) / len(cand_ngrams)) * 100 if cand_ngrams else 0
    
    # Check if URL or shortcode is in history
    url = item.get('source_url', '')
    shortcode = url.split('/')[-2] if '/' in url.strip('/') else ''
    url_in_hist = (url in history_text) or (shortcode and shortcode in history_text)
    
    if sim > 15.0 or len(common) >= 3 or url_in_hist:
        dupe_items.append((idx, item['title'], item['source_page'], sim, len(common), url_in_hist))
    else:
        fresh_items.append(item)

print(f"\nFresh items: {len(fresh_items)} / 42")
print(f"Duplicate/Old items: {len(dupe_items)} / 42")
print("\n--- Duplicate Items Found in History ---")
for idx, title, page, sim, comm, in_hist in dupe_items:
    print(f"Item {idx+1}: {title} ({page}) | Sim: {sim:.1f}%, 4-grams: {comm}, url_in_hist: {in_hist}")
