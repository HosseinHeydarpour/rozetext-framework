import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
BASE_DIR = 'd:/rozetext-framework'
sys.path.insert(0, BASE_DIR)
from scripts.anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine.get_instance()
with open('data/hunted-42-reels-batch.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

print(f'Total in batch: {len(batch)}')
clean_items = []
for i, item in enumerate(batch):
    raw = item.get('extracted_raw_text') or item.get('content') or ''
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    res = engine.check(raw)
    is_dup = res['is_duplicate']
    views = item.get('source_views', '')
    url = item.get('source_url', '')
    page = item.get('source_page', '')
    hook = lines[0] if lines else ''
    sim = res['similarity_score']
    if not is_dup and 7 <= len(lines) <= 16:
        clean_items.append((i, item, sim, len(lines)))
        print(f"CLEAN [{i}] Sim: {sim}% | Lines: {len(lines)} | Views: {views[:25]} | Page: {page} | Hook: {hook[:35]}")
    else:
        status = 'DUP' if is_dup else f'LINES={len(lines)}'
        reason = res.get('match_reason', '-')[:35]
        print(f"REJECT [{i}] {status} | Sim: {sim}% | Reason: {reason} | Hook: {hook[:30]}")

print(f"\nTotal Clean Pass from this file: {len(clean_items)}")
