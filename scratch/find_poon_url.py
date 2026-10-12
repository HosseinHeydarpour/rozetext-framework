import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
fdir = r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c'
for root, dirs, files in os.walk(fdir):
    for f in files:
        if 'snapshot' in f:
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                c = fh.read()
            if 'poon_text' in c:
                m = re.findall(r'url="([^"]+)"', c)
                for u in set(m):
                    if 'reel' in u or '/p/' in u:
                        print(f"{f}: {u}")
