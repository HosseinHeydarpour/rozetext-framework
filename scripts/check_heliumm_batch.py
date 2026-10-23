import json, sys
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open('data/hunted-42-reels-batch.json', encoding='utf-8'))
for idx in [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24]:
    r = d[idx]
    raw = r.get('extracted_raw_text', '')
    lines = [l for l in raw.strip().split('\n') if l.strip()]
    print(f"IDX {idx}: {len(lines)} lines | {r.get('source_views')} | {r.get('source_url')}")
    print("   ", raw.strip().replace('\n', ' // ')[:140])
