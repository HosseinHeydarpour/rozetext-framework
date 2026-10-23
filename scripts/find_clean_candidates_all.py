import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine.get_instance()
print(f"Loaded corpus size: {len(engine.corpus)}")

json_files = glob.glob('data/*.json')
all_items = []
seen_urls = set()
seen_contents = set()

for path in json_files:
    if 'benchmark' in path or 'harvest' in path or 'scripts-db' in path or 'all_harvested' in path:
        continue
    try:
        data = json.load(open(path, encoding='utf-8'))
        items = data if isinstance(data, list) else data.get('scripts', [])
        for it in items:
            url = it.get('source_url', '')
            content = it.get('content', '')
            if not content: continue
            if url in seen_urls or content in seen_contents:
                continue
            seen_urls.add(url)
            seen_contents.add(content)
            all_items.append((path, it))
    except Exception as e:
        pass

print(f"Total unique candidates collected: {len(all_items)}")

clean_candidates = []
for file_origin, it in all_items:
    txt = it['content']
    res = engine.check(txt)
    is_dup = res.get('is_duplicate', False)
    sim = res.get('similarity_score', 0.0)
    page = it.get('source_page', '')
    
    # Exclude @vahidrezakhoshbayan monopoly
    if page == '@vahidrezakhoshbayan':
        continue
        
    if not is_dup and sim < 38.0:
        lines = [l for l in txt.split('\n') if l.strip()]
        if 6 <= len(lines) <= 18:
            clean_candidates.append({
                'origin': file_origin,
                'title': it.get('title', ''),
                'source_page': page,
                'source_url': it.get('source_url', ''),
                'source_views': it.get('source_views', ''),
                'lines_count': len(lines),
                'sim': sim,
                'content': txt,
                'item': it
            })

print(f"Clean, non-duplicate, non-vahidreza candidates: {len(clean_candidates)}")

# Group by page
from collections import Counter
pages = [c['source_page'] for c in clean_candidates]
print("Distribution by page:", Counter(pages))

with open('data/clean_pool_discovered.json', 'w', encoding='utf-8') as f:
    json.dump([c['item'] for c in clean_candidates], f, ensure_ascii=False, indent=2)
print("Saved to data/clean_pool_discovered.json")
