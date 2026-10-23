import json
import glob
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine.get_instance()

# Check what's in data/clean_pool_discovered.json
print("=== clean_pool_discovered.json ===")
try:
    with open('data/clean_pool_discovered.json', 'r', encoding='utf-8') as f:
        clean_pool = json.load(f)
    for it in clean_pool:
        c = it.get('content', '')
        res = engine.check(c)
        title = it.get('title')
        views = it.get('source_views')
        page = it.get('source_page')
        dup = res['is_duplicate']
        sim = res['similarity_score']
        print(f"Title: {title} | Views: {views} | Page: {page} | Dup: {dup} | Sim: {sim}%")
except Exception as e:
    print(f"Error reading clean_pool_discovered.json: {e}")

# Check harvest files (e.g. harvest_text.love400.json, harvest____yeharf.json, etc.)
harvest_files = glob.glob('data/harvest_*.json')
print(f"\n=== Found {len(harvest_files)} harvest files ===")
for hf in harvest_files:
    fname = os.path.basename(hf)
    try:
        with open(hf, 'r', encoding='utf-8') as f:
            items = json.load(f)
        clean_count = 0
        samples = []
        for it in items:
            txt = it.get('text', '')
            if len(txt.splitlines()) >= 5 or len(txt) > 80:
                res = engine.check(txt)
                if not res['is_duplicate']:
                    clean_count += 1
                    if len(samples) < 2:
                        samples.append((it.get('href'), txt[:60].replace('\n', ' ')))
        print(f"{fname}: total={len(items)} | clean={clean_count} | samples={samples}")
    except Exception as e:
        print(f"{fname}: error {e}")
