import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
dir_p = r"C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch"
for fname in ['blind_eval_part1.json', 'blind_eval_part2.json', 'blind_eval_part3.json']:
    fpath = os.path.join(dir_p, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        items = json.load(f)
    print(f"=== {fname}: {len(items)} items ===")
    if isinstance(items, dict):
        print("  Keys:", list(items.keys())[:10])
    else:
        for it in items[:10]:
            sc = it.get('shortcode')
            v = it.get('views')
            txt = it.get('video_text') or it.get('text') or ''
            print(f"  {sc} | {v} | {txt[:50]}...")
