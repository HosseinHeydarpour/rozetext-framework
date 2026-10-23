import asyncio
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine

async def harvest_reels_from_profile(username, max_scrolls=10):
    cdp = ChromeCDP()
    await cdp.connect()
    sid = await cdp.attach_page('DD1DF7845B8CDAC41D5884C86D74F67F')
    
    url = f"https://www.instagram.com/{username}/reels/"
    print(f"[*] Navigating to {url}...")
    await cdp.navigate(sid, url)
    await asyncio.sleep(4)
    
    # Scroll down to load more
    for i in range(max_scrolls):
        await cdp.evaluate(sid, "window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(1.5)
        
    js = """
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
        const seen = new Set();
        const results = [];
        for (const a of anchors) {
            const href = a.getAttribute('href');
            if (!href || seen.has(href)) continue;
            seen.add(href);
            // play count is usually in a span inside or innerText
            const text = a.innerText.trim();
            results.push({
                href: href,
                text: text
            });
        }
        return results;
    })()
    """
    reels = await cdp.evaluate(sid, js)
    print(f"[*] Harvested {len(reels)} unique reels from @{username}")
    await cdp.close()
    return reels

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "___yeharf"
    reels = asyncio.run(harvest_reels_from_profile(username, 5))
    with open(f"data/harvest_{username}.json", "w", encoding="utf-8") as f:
        json.dump(reels, f, ensure_ascii=False, indent=2)
    print(f"Saved to data/harvest_{username}.json")
