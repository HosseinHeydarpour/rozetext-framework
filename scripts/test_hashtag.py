import asyncio
import sys, os, json, urllib.parse
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

async def test_hashtag(tag):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '') or 'Instagram' in t.get('title', '')]
    if not ig_targets:
        print("No Instagram target found. All targets:", targets)
        await cdp.close()
        return

    target = ig_targets[0]
    print(f"Target found: {target.get('title')} ({target.get('url')})")
    sid = await cdp.attach_page(target['targetId'])
    
    encoded_tag = urllib.parse.quote(tag)
    url = f"https://www.instagram.com/explore/tags/{encoded_tag}/"
    print(f"Navigating to {url} ...")
    await cdp.navigate(sid, url)
    await asyncio.sleep(6)
    
    script = """
    (() => {
        let links = Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/p/"]')).map(a => a.href);
        let title = document.title;
        return {
            title: title,
            url: window.location.href,
            linksCount: links.length,
            links: Array.from(new Set(links)).slice(0, 30)
        };
    })()
    """
    res = await cdp.evaluate(sid, script)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    tag = "تکست_سنگین"
    asyncio.run(test_hashtag(tag))
