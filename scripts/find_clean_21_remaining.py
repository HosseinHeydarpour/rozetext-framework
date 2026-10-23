import sys, os, json
sys.path.insert(0, os.path.abspath('.'))
from scripts.anti_duplication import AntiDuplicationEngine

def main():
    engine = AntiDuplicationEngine.get_instance()
    db = json.load(open('data/scripts-db.json', encoding='utf-8'))
    db_urls = {s.get('source_url') for s in db['scripts'] if s.get('source_url')}
    
    print(f"Current db scripts: {len(db['scripts'])}")
    print(f"Current db URLs: {len(db_urls)}")
    
    # 1. From hunted-42-fresh-multiaccount-verified.json
    d42 = json.load(open('data/hunted-42-fresh-multiaccount-verified.json', encoding='utf-8'))
    candidates = [x for x in d42 if x.get('source_url') not in db_urls]
    
    clean_pool = json.load(open('data/clean_pool_discovered.json', encoding='utf-8'))
    for x in clean_pool:
        if x.get('source_url') not in db_urls and x.get('source_url') not in [c.get('source_url') for c in candidates]:
            candidates.append(x)
            
    print(f"Total candidate pool: {len(candidates)}")
    
    verified = []
    seen_urls = set()
    for c in candidates:
        u = c.get('source_url')
        if u in seen_urls:
            continue
        text = c.get('extracted_raw_text') or c.get('content')
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if not (7 <= len(lines) <= 17):
            continue
        res = engine.check(text)
        if not res.get('is_valid', True):
            continue
        seen_urls.add(u)
        verified.append(c)
        
    print(f"Total verified candidates ready to schedule: {len(verified)}")
    for i, v in enumerate(verified):
        print(f"{i+1:2d}. {v.get('source_page')} | {v.get('source_views')} | lines: {len([l for l in v.get('content').splitlines() if l.strip()]):2d} | {v.get('title')[:40]}")

if __name__ == '__main__':
    main()
