import json
import glob
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

all_cands = {}
for fpath in glob.glob('downloads/*_high*.json'):
    account = os.path.basename(fpath).replace('_high.json', '').replace('_deep_high.json', '').replace('_high_reels.json', '')
    with open(fpath, encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        code = item.get('code')
        if not code:
            continue
        vnum = item.get('views_num', 0)
        vstr = item.get('views_str', '')
        if code not in all_cands:
            all_cands[code] = {
                'code': code,
                'account': account,
                'views_num': vnum,
                'views_str': vstr,
                'url': item.get('href') or f"https://www.instagram.com/reel/{code}/"
            }

print(f"Total unique candidates in downloads: {len(all_cands)}")
sorted_cands = sorted(all_cands.values(), key=lambda x: x['views_num'], reverse=True)

for c in sorted_cands:
    frame_exists = os.path.exists(f"downloads/frames/{c['code']}_frame.png")
    print(f"{c['code']:<15} | {c['views_str']:<8} | {c['account']:<15} | Frame: {frame_exists}")
