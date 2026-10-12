import os, sys, re, glob
sys.stdout.reconfigure(encoding='utf-8')

dirs = ['.', r'D:\rozetext content']
target_ids = [
    "DHOoHu0IiOA", "DGvs7wdI8m9", "DGYhwC9osq5", "DGQzWJsoXkB",
    "DF-yFaKo9mG", "DFavqaEIMl_", "DFVldo0ITUD", "DEaZbyVoEze",
    "DDuqExPo0xZ", "DDpblWFow7g"
]

print("Searching for target IDs in files...")
found = {}

for d in dirs:
    for root, _, files in os.walk(d):
        if 'node_modules' in root or '.git' in root or '__pycache__' in root:
            continue
        for f in files:
            if f.endswith(('.py', '.json', '.txt', '.md')):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                    for tid in target_ids:
                        if tid in content:
                            found.setdefault(tid, []).append(fp)
                except Exception:
                    pass

for tid in target_ids:
    print(f"- {tid}: found in {found.get(tid, [])}")
