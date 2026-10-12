import os, glob, sys, re
sys.stdout.reconfigure(encoding='utf-8')

codes = [
    'DPjl0mTCIps', 'DPeaox9CPJk', 'DO_homTiPTp', 'DNtMbWm0P4y',
    'DMqPqQCIem7', 'DIJ0fkOoP5I', 'DHOoHu0IiOA', 'DGvs7wdI8m9',
    'DGYhwC9osq5', 'DGQzWJsoXkB', 'DF-yFaKo9mG', 'DFavqaEIMl_',
    'DFVldo0ITUD', 'DEaZbyVoEze', 'DDuqExPo0xZ', 'DDpblWFow7g'
]

search_dirs = [
    r'D:\rozetext-framework',
    r'D:\rozetext content',
    r'C:\Users\User\.gemini\antigravity\brain'
]

found_texts = {c: [] for c in codes}

for sdir in search_dirs:
    if not os.path.exists(sdir):
        continue
    for root, dirs, files in os.walk(sdir):
        for f in files:
            if f.endswith(('.json', '.txt', '.md', '.py', '.jsonl')):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                    for c in codes:
                        if c in content:
                            found_texts[c].append(fpath)
                except Exception:
                    pass

print("=== SEARCH RESULTS FOR 16 CODES ===")
for c, paths in found_texts.items():
    print(f"Code: {c} -> found in {len(paths)} files")
    for p in paths[:3]:
        print(f"   {p}")
