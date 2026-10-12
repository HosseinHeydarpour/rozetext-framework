import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

prompt_path = r'D:\rozetext content\prompt.md'
if os.path.exists(prompt_path):
    with open(prompt_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    print("prompt.md size:", len(text))
    # search for instagram urls
    urls = re.findall(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', text)
    print("Instagram reel URLs in prompt.md:", len(urls))
    for u in urls[:10]:
        print(" ", u)
