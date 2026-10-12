import json, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json'
with open(p, 'r', encoding='utf-8') as f:
    items = json.load(f)

cands = ['DO6YkXMCOCC', 'DJ7IO05olRX', 'DJR63KJIy2t', 'DPHRC0yCJxg', 'DIWun0Zo1Dt', 'DHlzMLlI6Ry']
for it in items:
    if it.get('shortcode') in cands:
        print('==================================================')
        print(it.get('shortcode'), it.get('views'), it.get('account'))
        txt = it.get('video_text', '').strip('«»" \t\n')
        txt = re.sub(r'—\s*وحیدرضا خوش‌بیان.*$', '', txt).strip()
        print('TEXT:')
        print(txt)
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        print('LINES:', len(lines))
