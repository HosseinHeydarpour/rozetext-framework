import os, sys, glob, re, json
sys.stdout.reconfigure(encoding='utf-8')

codes = ['DduAM8dqIck', 'DdtnLLDqHGi', 'Dds-LJRTFw7']

# Search everywhere
for sdir in [r'C:\Users\User\.gemini\antigravity\brain', r'D:\rozetext-framework']:
    for root, dirs, files in os.walk(sdir):
        for f in files:
            if f.endswith(('.json', '.txt', '.md', '.jsonl')):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
                        c = fp.read()
                    for code in codes:
                        if code in c and not f.endswith('review.md'):
                            print(f"{code} in {fpath}")
                            # show context around code
                            idx = c.find(code)
                            print(c[max(0, idx-100):min(len(c), idx+200)])
                            print("="*40)
                except:
                    pass
