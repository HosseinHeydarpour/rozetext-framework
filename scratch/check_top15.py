import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\rozetext content\top_15_viral_delneveshte_reels.txt'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    print("top_15 size:", len(text))
    urls = re.findall(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', text)
    print("Instagram reel URLs:", len(urls))
    for u in urls:
        idx = text.find(u)
        block = text[max(0, idx-100):min(len(text), idx+600)]
        print(f"--- {u} ---")
        print(block[:300])
