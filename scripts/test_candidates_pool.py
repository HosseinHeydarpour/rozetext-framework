import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

path = r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\candidates_32_data.json'
with open(path, 'r', encoding='utf-8') as f:
    items = json.load(f)

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_scs = {s.get('source_url', '').strip().rstrip('/').split('/')[-1] for s in db.get('scripts', [])}

for it in items:
    sc = it.get('shortcode')
    acc = it.get('account')
    v = str(it.get('views'))
    text = it.get('caption', '') or it.get('ogDesc', '')
    is_1m = ('M' in v or 'میلیون' in v) and not ('0.' in v)
    if is_1m:
        res = ENGINE.check_duplicate_against_history(text, text)
        in_db = sc in existing_scs
        print(f"{sc} | {acc} | {v} | in_db={in_db} | dup_hist={res['is_duplicate']} ({res['similarity_score']}%)")
