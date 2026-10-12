import os, sys
sys.stdout.reconfigure(encoding='utf-8')

brain_root = r'C:\Users\User\.gemini\antigravity\brain'
entries = os.listdir(brain_root)
print(f"Top-level entries in brain: {len(entries)}")

interesting_files = []

for entry in entries:
    ep = os.path.join(brain_root, entry)
    if os.path.isdir(ep):
        for root, dirs, files in os.walk(ep):
            for f in files:
                lf = f.lower()
                if any(k in lf for k in ['candidate', 'hunted', 'reel', 'batch', 'transcript', 'vahid']):
                    if lf.endswith('.json') or lf.endswith('.txt'):
                        fp = os.path.join(root, f)
                        interesting_files.append((fp, os.path.getsize(fp)))

print(f"Found {len(interesting_files)} interesting files:")
for fp, sz in sorted(interesting_files, key=lambda x: x[1], reverse=True)[:30]:
    print(f"- {sz:8d} bytes: {fp}")
