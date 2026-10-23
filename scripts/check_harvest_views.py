import json
import glob
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def parse_v(t):
    if not t: return 0
    t = str(t).replace(',', '').strip()
    if 'M' in t:
        return float(t.replace('M', '')) * 1000000
    if 'K' in t:
        return float(t.replace('K', '')) * 1000
    try:
        return float(t)
    except:
        return 0

for p in glob.glob('data/harvest_*.json'):
    with open(p, encoding='utf-8') as f:
        d = json.load(f)
    high = [item for item in d if parse_v(item.get('text')) >= 300000]
    print(f"{os.path.basename(p)}: {len(high)} high items >= 300K")
    for item in high[:5]:
        print(f"   {item.get('href')} | {item.get('text')}")
