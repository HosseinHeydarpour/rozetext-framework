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

batch_files = [
    'data/hunted-42-reels-batch-verified.json',
    'data/hunted-42-fresh-multiaccount-verified.json',
    'data/hunted-42-reels-batch.json',
    'data/hunted-21-verified-from-tuesday.json',
    'data/hunted-12-reels-batch-2026-10-11.json',
    'data/hunted-batch-2026-09-29-4days.json',
    'data/hunted-batch-2026-10-03.json',
    'data/hunted-batch-2026-09-28.json'
]

clean_cands = []

for bf in batch_files:
    if not os.path.exists(bf):
        continue
    try:
        with open(bf, 'r', encoding='utf-8') as f:
            items = json.load(f)
        if isinstance(items, dict):
            items = items.get('scripts', []) or items.get('reels', []) or list(items.values())
        print(f"\nChecking {bf} ({len(items)} items)...")
        for it in items:
            text = it.get('content') or it.get('extracted_raw_text') or ''
            if not text:
                continue
            
            # Check length: at least 6 lines
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            if len(lines) < 6:
                continue

            # Anti-duplication check
            res = engine.check(text)
            if not res['is_duplicate']:
                # Views check
                views = it.get('source_views') or it.get('views') or 0
                clean_cands.append({
                    'file': os.path.basename(bf),
                    'title': it.get('title'),
                    'archetype': it.get('archetype'),
                    'goal': it.get('goal'),
                    'source_page': it.get('source_page'),
                    'source_url': it.get('source_url'),
                    'source_views': views,
                    'similarity': res['similarity_score'],
                    'lines_count': len(lines),
                    'hook': lines[0] if lines else '',
                    'content': text,
                    'caption': it.get('caption', '')
                })
    except Exception as e:
        print(f"Error {bf}: {e}")

print(f"\n==========================================")
print(f"Total CLEAN items found from batches: {len(clean_cands)}")
print(f"==========================================")
for i, c in enumerate(clean_cands[:30]):
    print(f"{i+1}. [{c['source_page']}] ({c['source_views']}) Sim: {c['similarity']}% | Lines: {c['lines_count']} | Hook: {c['hook'][:40]} | File: {c['file']}")
