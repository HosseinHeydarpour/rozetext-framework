import sys, re
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\.tempmediaStorage\snapshot_1790243469520.txt', 'r', encoding='utf-8') as f:
    text = f.read()

urls = re.findall(r'url="([^"]+)"', text)
for u in set(urls):
    if 'reel' in u:
        print("Reel URL:", u)
