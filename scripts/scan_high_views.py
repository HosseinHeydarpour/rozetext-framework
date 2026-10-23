import json
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

all_reels = {}

for fpath in glob.glob('data/*.json'):
    if any(k in fpath for k in ['scripts-db', 'stories-db', 'telegram', 'benchmark_accounts']):
        continue
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            d = json.load(f)
            items = []
            if isinstance(d, list):
                items = d
            elif isinstance(d, dict):
                if 'reels' in d: items = d['reels']
                elif 'items' in d: items = d['items']
                elif 'candidates' in d: items = d['candidates']
                else: items = list(d.values())
            for item in items:
                if isinstance(item, dict):
                    sc = item.get('shortcode') or item.get('id') or item.get('code')
                    if sc and 9 <= len(sc) <= 13:
                        views = item.get('views') or item.get('view_count') or item.get('play_count') or 0
                        if isinstance(views, str):
                            v_clean = views.replace(',', '').replace(' ', '').replace('بازدید', '').replace('views', '').replace('view', '')
                            try:
                                if 'M' in v_clean.upper():
                                    views = int(float(v_clean.upper().replace('M', '')) * 1_000_000)
                                elif 'K' in v_clean.upper():
                                    views = int(float(v_clean.upper().replace('K', '')) * 1_000)
                                else:
                                    views = int(v_clean)
                            except:
                                views = 0
                        if sc not in all_reels or views > (all_reels[sc].get('views') or 0):
                            all_reels[sc] = {
                                'shortcode': sc,
                                'views': views,
                                'owner': item.get('owner') or item.get('source_page') or item.get('author'),
                                'caption': item.get('caption') or item.get('text') or '',
                                'source_file': os.path.basename(fpath),
                                'video_url': item.get('video_url')
                            }
    except Exception as e:
        pass

print(f'Total unique shortcodes found: {len(all_reels)}')
high_views = [r for r in all_reels.values() if (r['views'] or 0) >= 450_000]
print(f'Reels with >= 450K views: {len(high_views)}')
high_views_sorted = sorted(high_views, key=lambda x: x['views'] or 0, reverse=True)
for i, r in enumerate(high_views_sorted[:40]):
    sc = r['shortcode']
    vw = r['views']
    ow = r['owner']
    sf = r['source_file']
    cap = r['caption'][:40].replace('\n', ' ')
    print(f'{i+1}. sc={sc} | views={vw} | owner={ow} | file={sf} | cap={cap}')
