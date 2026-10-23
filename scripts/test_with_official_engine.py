import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine.get_instance()
print(f"Loaded corpus size in AntiDuplicationEngine: {len(engine.corpus)}")

items = json.load(open('data/hunted-42-fresh-multiaccount-verified.json', encoding='utf-8'))

passed = []
failed = []

for idx, it in enumerate(items):
    txt = it['content']
    res = engine.check(txt)
    is_dup = res.get('is_duplicate', False)
    sim = res.get('similarity_score', 0.0)
    reason = res.get('match_reason', '')
    doc = res.get('matched_document', {})
    
    if is_dup:
        failed.append((idx, it['title'], it['source_page'], sim, reason, doc.get('identifier', '')))
    else:
        passed.append((idx, it['title'], it['source_page'], sim, doc.get('identifier', '')))

print(f"\nPassed (Non-duplicate): {len(passed)} / {len(items)}")
print(f"Failed (Duplicate): {len(failed)} / {len(items)}")

print("\n--- Failed Details ---")
for idx, title, page, sim, reason, doc_id in failed:
    print(f"Item {idx+1}: {title} ({page}) -> {sim:.1f}% ({reason}) with {doc_id}")
