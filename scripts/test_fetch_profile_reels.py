import asyncio
import sys, os, json
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

async def check_profile():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    print("Navigating to https://www.instagram.com/leyli_geraphy/reels/ ...")
    await cdp.navigate(sid, "https://www.instagram.com/leyli_geraphy/reels/")
    await asyncio.sleep(5)
    
    script = """
    (() => {
        // Collect all reel links and their view counts
        let items = [];
        let links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
        for (let a of links) {
            let href = a.href;
            let spans = Array.from(a.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean);
            items.append ? items.push({href: href, spans: spans}) : items.push({href: href, spans: spans});
        }
        return {
            totalLinks: links.length,
            items: items.slice(0, 15)
        };
    })()
    """
    res = await cdp.evaluate(sid, script)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(check_profile())
