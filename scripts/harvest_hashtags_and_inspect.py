import asyncio
import sys, os, json, urllib.parse, base64
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

HASHTAGS = [
    "تکست_سنگین",
    "دلنوشته_خاص",
    "حرف_دل",
    "آدم_امن",
    "خداحافظی_آرام"
]

async def harvest_tags():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '') or 'Instagram' in t.get('title', '')]
    if not ig_targets:
        print("No IG target")
        await cdp.close()
        return
        
    sid = await cdp.attach_page(ig_targets[0]['targetId'])
    os.makedirs("downloads/frames", exist_ok=True)
    
    all_links = set()
    for tag in HASHTAGS:
        encoded = urllib.parse.quote(tag)
        url = f"https://www.instagram.com/explore/tags/{encoded}/"
        print(f"\n[TAG] Navigating to #{tag}...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4)
        
        # Scroll once
        await cdp.evaluate(sid, "window.scrollBy(0, 1000)")
        await asyncio.sleep(2)
        
        script = """
        (() => {
            let links = Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]')).map(a => a.href);
            return Array.from(new Set(links));
        })()
        """
        links = await cdp.evaluate(sid, script)
        print(f"  Found {len(links or [])} links in #{tag}")
        for l in (links or []):
            all_links.add((l, tag))
            
    print(f"\n[TOTAL] Collected {len(all_links)} total unique links from all hashtags!")
    
    # Save list to file
    items = [{"url": l, "tag": t, "shortcode": l.strip('/').split('/')[-1]} for l, t in all_links]
    with open("data/hashtag_candidates.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
        
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(harvest_tags())
