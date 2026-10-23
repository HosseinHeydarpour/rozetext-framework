import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine

async def inspect_reel(shortcode):
    cdp = ChromeCDP()
    await cdp.connect()
    sid = await cdp.attach_page('DD1DF7845B8CDAC41D5884C86D74F67F')
    
    url = f"https://www.instagram.com/reel/{shortcode}/"
    print(f"Navigating to {url}...")
    await cdp.navigate(sid, url)
    await asyncio.sleep(4)
    
    # Take screenshot of the reel
    os.makedirs("artifacts/reels_screenshots", exist_ok=True)
    shot_path = f"artifacts/reels_screenshots/{shortcode}.png"
    await cdp.capture_screenshot(sid, shot_path)
    print(f"Screenshot saved to {shot_path}")
    
    # Extract page metadata, caption, title
    js = """
    (() => {
        const title = document.title;
        // Find caption text
        const captionEls = Array.from(document.querySelectorAll('h1, span._ap3a, div._a9zs, div[role="button"] span'));
        const texts = captionEls.map(e => e.innerText.trim()).filter(Boolean);
        return {
            title: title,
            texts: texts.slice(0, 10)
        };
    })()
    """
    meta = await cdp.evaluate(sid, js)
    print("Meta:", json.dumps(meta, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    code = sys.argv[1] if len(sys.argv) > 1 else "DcGUbIrt1Yc"
    asyncio.run(inspect_reel(code))
