import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

from server import PublisherEngine

engine = PublisherEngine()

with open('published-content-history.md', 'r', encoding='utf-8') as f:
    history_text = f.read()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Extract individual reels from history
reels_blocks = re.split(r'### Reel #(\d+)', history_text)[1:]
reels = {}
for i in range(0, len(reels_blocks), 2):
    num = int(reels_blocks[i])
    block = reels_blocks[i+1]
    reels[num] = block

print(f"Total published reels parsed: {len(reels)}")

today_slots = [s for s in db['scripts'] if s.get('scheduled_date') == '2026-10-06' and s.get('scheduled_slot') in [5, 6]]

for s in today_slots:
    content = s['content']
    slot = s['scheduled_slot']
    title = s['title']
    
    res = engine.check_duplicate_against_history(content, content)
    is_dup = res["is_duplicate"]
    max_sim = res["similarity_score"]
    closest_match = res["duplicate_of_reel"]
    
    # Also find top 3 closest reels in history manually for full transparency
    words = set(re.findall(r'[\w\u0600-\u06FF]+', content.lower()))
    similarities = []
    for num, block in reels.items():
        hist_words = set(re.findall(r'[\w\u0600-\u06FF]+', block.lower()))
        if not hist_words:
            continue
        inter = words.intersection(hist_words)
        jaccard = (len(inter) / len(words)) * 100 if words else 0
        similarities.append((num, jaccard, list(inter)[:5]))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n================ SLOT {slot} ================")
    print(f"Title: {title}")
    print(f"Server check_duplicate_against_history result:")
    print(f"  - Is Duplicate: {is_dup} (Threshold is 45.0%)")
    print(f"  - Max Similarity: {max_sim:.1f}%")
    print(f"  - Closest match: {closest_match}")
    print(f"Top 3 closest historical reels:")
    for num, sim, common_words in similarities[:3]:
        print(f"  - Reel #{num}: {sim:.1f}% overlap (Common words: {', '.join(common_words)})")
