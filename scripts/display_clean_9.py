import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json'
items = json.load(open(p, encoding='utf-8'))
clean_indices = [6, 12, 14, 18, 20, 22, 23, 24, 27]

for idx in clean_indices:
    it = items[idx]
    txt = it.get('video_text', '').strip()
    lines = [line.strip() for line in txt.split('\n') if line.strip()]
    sc = it.get('shortcode')
    views = it.get('views')
    author = it.get('author')
    url = it.get('url')
    print(f"=== Index [{idx}]: {sc} | Views: {views} | Author: {author} | Lines: {len(lines)} ===")
    print(f"URL: {url}")
    print("Full text:")
    print(txt)
    print("-" * 50)
