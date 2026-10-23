import json
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

frames = glob.glob('downloads/frames/*.png')
print(f"Total frame png files in downloads/frames: {len(frames)}")

# Load all known reels from pool files
reels_map = {}
for p in ['data/all_harvested_ranked.json', 'data/fresh_live_hunted_pool.json', 'data/expanded_hunted_pool.json', 'data/golden_inspected_pool.json', 'data/batch_inspected_top15.json', 'data/fresh_harvested_batch.json']:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            items = json.load(f)
        for it in items:
            sc = it.get('shortcode')
            if sc:
                views = it.get('views') or 0
                if isinstance(views, str):
                    try:
                        v = views.replace(',', '').replace(' ', '').replace('M', '000000').replace('K', '000')
                        views = int(v)
                    except:
                        views = 0
                if sc not in reels_map or views > reels_map[sc].get('views', 0):
                    reels_map[sc] = {
                        'shortcode': sc,
                        'account': it.get('account'),
                        'url': it.get('url'),
                        'views': views,
                        'views_str': it.get('views_str')
                    }

# Find which frames correspond to known reels
matched_frames = []
for fr in frames:
    base = os.path.basename(fr)
    # extract shortcode
    sc = base.split('_')[0]
    info = reels_map.get(sc, {})
    matched_frames.append({
        'path': fr,
        'filename': base,
        'shortcode': sc,
        'account': info.get('account'),
        'url': info.get('url') or f"https://www.instagram.com/reel/{sc}/",
        'views': info.get('views', 0),
        'views_str': info.get('views_str')
    })

# Sort by views desc
matched_frames = sorted(matched_frames, key=lambda x: x['views'], reverse=True)

print(f"Matched {len(matched_frames)} frames.")
print("\nTop 40 frames by views:")
seen_sc = set()
for i, m in enumerate(matched_frames):
    if m['shortcode'] in seen_sc:
        continue
    seen_sc.add(m['shortcode'])
    print(f"{len(seen_sc)}. sc={m['shortcode']} | views={m['views']:,} ({m['views_str']}) | account={m['account']} | frame={m['filename']}")
    if len(seen_sc) >= 50:
        break
