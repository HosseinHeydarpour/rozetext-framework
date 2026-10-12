import sys, os, json, glob, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_db_texts = []
for s in db.get('scripts', []):
    t = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if t.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), t.strip()))

target_files = [
    r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\new_top_50_reels.json",
    r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\verify_27_data.json",
    r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\verify_4_data.json",
    r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\new_reels_history.json",
    r"C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\batch2_wave1_29.json",
    r"C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\blind_eval_part1.json",
    r"C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\blind_eval_part2.json",
    r"C:\Users\User\.gemini\antigravity\brain\05648e36-121e-4f64-aea4-a0500cb6c2a9\scratch\blind_eval_part3.json"
]

target_files.extend(glob.glob(r"C:\Users\User\.gemini\antigravity\brain\727a329c-ae5d-47f3-930f-a557f52abe67\*.md"))

valid_pool = {}

for tf in target_files:
    if not os.path.exists(tf):
        continue
    if tf.endswith('.json'):
        try:
            with open(tf, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get('reels', data.get('scripts', data.get('items', [])))
        for it in items:
            if not isinstance(it, dict): continue
            txt = it.get('extracted_raw_text') or it.get('content') or it.get('text') or ''
            views = str(it.get('source_views') or it.get('views') or '')
            u = it.get('source_url', '') or it.get('url', '')
            sc = it.get('shortcode') or (u.rstrip('/').split('/')[-1] if u else '')
            page = it.get('source_page', '') or it.get('account', '')
            
            # check views >= 1M
            is_1m = ('M' in views or 'میلیون' in views or '10,' in views or '1,' in views) and not ('0.' in views)
            if not is_1m:
                continue
            lines = [l.strip() for l in txt.splitlines() if l.strip()]
            if len(lines) < 7 or len(lines) > 16:
                continue
            bad_words = ['مولانا', 'شمس', 'دختر', 'پسر', 'تولد', 'نوروز', 'یلدا']
            if any(bw in txt for bw in bad_words):
                continue
            if 'halekhoub' in page:
                continue
                
            res_hist = ENGINE.check_duplicate_against_history(txt, txt)
            if res_hist['is_duplicate']:
                continue
                
            c_tokens = ENGINE._normalize_persian_tokens(txt)
            c_ngrams = ENGINE._extract_ngrams(txt, 4)
            db_dup = False
            for s_id, s_title, s_txt in existing_db_texts:
                s_tokens = ENGINE._normalize_persian_tokens(s_txt)
                overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
                s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
                common_ngrams = c_ngrams & s_ngrams
                if len(common_ngrams) >= 2 or overlap >= 0.40:
                    db_dup = True
                    break
            if db_dup:
                continue
                
            k = sc if sc else lines[0]
            if k not in valid_pool:
                valid_pool[k] = {
                    'shortcode': sc,
                    'url': u,
                    'views': views,
                    'page': page,
                    'lines': len(lines),
                    'content': txt,
                    'title': it.get('title') or lines[0],
                    'file': os.path.basename(tf)
                }

print(f"\nTOTAL FOUND IN TARGET FILES: {len(valid_pool)}\n")
for k, v in valid_pool.items():
    print(f"[{v['shortcode']}] Views: {v['views']} | Lines: {v['lines']} | Page: {v['page']} | File: {v['file']}")
    print(v['content'].splitlines()[0][:40])
    print('------------------------------------')
