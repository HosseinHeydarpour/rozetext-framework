import asyncio
import sys, os, json, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

EXPANDED_TAGS = [
    "زخم_زبان",
    "احساس_اضافی_بودن",
    "تنهایی_پاییز",
    "بغض_سنگین",
    "آدم_اشتباه",
    "دلشکسته",
    "متن_غمگین_تنهایی"
]

async def harvest_fresh_tags():
    cdp = ChromeCDP()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Chrome...")
    while True:
        try:
            await cdp.connect()
            print("Connected!")
            break
        except Exception as e:
            print("Waiting for connection...")
            await asyncio.sleep(3)
            
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '') or 'Instagram' in t.get('title', '')]
    if not ig_targets:
        print("No IG target found!")
        await cdp.close()
        return
        
    sid = await cdp.attach_page(ig_targets[0]['targetId'])
    
    # Load existing candidates & DB
    existing_cands = json.load(open('data/hashtag_candidates.json', encoding='utf-8'))
    known_urls = {c['url'] for c in existing_cands}
    db = json.load(open('data/scripts-db.json', encoding='utf-8'))
    for s in db['scripts']:
        if s.get('source_url'):
            known_urls.add(s['source_url'])
            
    fresh_candidates = []
    
    for tag in EXPANDED_TAGS:
        tag_url = f"https://www.instagram.com/explore/tags/{tag}/"
        print(f"\n--- Scraping hashtag: #{tag} ---")
        try:
            await cdp.navigate(sid, tag_url)
            await asyncio.sleep(4)
            
            # Scroll down twice to load more reels
            for scroll in range(3):
                script = """
                (() => {
                    let links = Array.from(document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]'));
                    return links.map(a => a.href);
                })()
                """
                urls = await cdp.evaluate(sid, script)
                for u in urls:
                    if '/p/' in u or '/reel/' in u:
                        clean_u = u.split('?')[0]
                        if not clean_u.endswith('/'):
                            clean_u += '/'
                        parts = [p for p in clean_u.split('/') if p]
                        sc = parts[-1]
                        if clean_u not in known_urls:
                            known_urls.add(clean_u)
                            fresh_candidates.append({
                                "shortcode": sc,
                                "url": clean_u,
                                "tag": tag
                            })
                            print(f"  + Found candidate: {sc} (#{tag})")
                await cdp.evaluate(sid, "window.scrollBy(0, 1200);")
                await asyncio.sleep(2)
        except Exception as err:
            print(f"Error scraping #{tag}: {err}")
            
    print(f"\n[DONE] Total fresh candidates harvested: {len(fresh_candidates)}")
    combined = existing_cands + fresh_candidates
    with open('data/hashtag_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
        
    # Also save purely the fresh ones
    with open('data/fresh_hashtag_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(fresh_candidates, f, ensure_ascii=False, indent=2)
        
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(harvest_fresh_tags())
