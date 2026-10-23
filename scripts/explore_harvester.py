import asyncio
import sys, os, json
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

async def check_explore():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    print("Navigating to Explore page...")
    await cdp.navigate(sid, "https://www.instagram.com/explore/")
    await asyncio.sleep(5)
    
    script = """
    (() => {
        let links = Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]')).map(a => a.href);
        return Array.from(new Set(links)).slice(0, 30);
    })()
    """
    res = await cdp.evaluate(sid, script)
    print("Explore links found:", len(res or []))
    for r in (res or []):
        print("  ", r)
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(check_explore())
