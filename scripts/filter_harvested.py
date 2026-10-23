import glob, json

def parse_views(vstr):
    vstr = vstr.replace(',', '').strip()
    if not vstr: return 0
    if 'M' in vstr:
        return int(float(vstr.replace('M', '')) * 1_000_000)
    elif 'K' in vstr:
        return int(float(vstr.replace('K', '')) * 1_000)
    try:
        return int(vstr)
    except:
        return 0

all_reels = []
for p in glob.glob('data/harvest_*.json'):
    account = p.replace('data\\harvest_', '').replace('data/harvest_', '').replace('.json', '')
    data = json.load(open(p, encoding='utf-8'))
    for item in data:
        views = parse_views(item.get('text', ''))
        shortcode = item['href'].strip('/').split('/')[-1]
        all_reels.append({
            'account': account,
            'shortcode': shortcode,
            'url': f"https://www.instagram.com/reel/{shortcode}/",
            'views_str': item.get('text', ''),
            'views': views
        })

all_reels.sort(key=lambda x: x['views'], reverse=True)
print(f"Total harvested reels: {len(all_reels)}")
print(f"Reels >= 500K views: {len([r for r in all_reels if r['views'] >= 500_000])}")
print(f"Reels >= 200K views: {len([r for r in all_reels if r['views'] >= 200_000])}")

with open('data/all_harvested_ranked.json', 'w', encoding='utf-8') as f:
    json.dump(all_reels, f, ensure_ascii=False, indent=2)

for r in all_reels[:40]:
    print(f"{r['views_str']:>8} | @{r['account']:15} | {r['shortcode']} | {r['url']}")
