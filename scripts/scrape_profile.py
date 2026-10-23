import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def scrape_profile(username):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_target = None
    for t in targets:
        if "instagram.com" in t.get("url", ""):
            ig_target = t
            break
    if not ig_target:
        print("No IG tab found")
        await cdp.close()
        return []
    
    sid = await cdp.attach_page(ig_target["targetId"])
    profile_url = f"https://www.instagram.com/{username}/reels/"
    print(f"Navigating to {profile_url}...")
    await cdp.navigate(sid, profile_url)
    await asyncio.sleep(4)
    
    # Extract links and play/view counts
    js_extract = """
    (() => {
        const items = [];
        const links = document.querySelectorAll('a[href*="/reel/"], a[href*="/reels/"]');
        for (const a of links) {
            const href = a.getAttribute('href');
            if (!href) continue;
            // look for play count text inside
            const text = a.innerText || '';
            const spans = Array.from(a.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean);
            items.push({
                href: href,
                text: text,
                spans: spans
            });
        }
        return items;
    })()
    """
    reels = await cdp.evaluate(sid, js_extract)
    print(f"Found {len(reels)} reel elements on page.")
    await cdp.close()
    return reels

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "text.love400"
    reels = asyncio.run(scrape_profile(user))
    print(json.dumps(reels[:15], ensure_ascii=False, indent=2))
