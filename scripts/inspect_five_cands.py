import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from chrome_cdp import ChromeCDP

async def inspect_five():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
    
    cands = [
        {"shortcode": "DeHxCX3i3xc", "url": "https://www.instagram.com/shadighorbanyy/reel/DeHxCX3i3xc/", "acc": "@shadighorbanyy", "views": "1.2M"},
        {"shortcode": "DdzFv9hCAZO", "url": "https://www.instagram.com/shadighorbanyy/reel/DdzFv9hCAZO/", "acc": "@shadighorbanyy", "views": "663K"},
        {"shortcode": "DcRbdTOsajM", "url": "https://www.instagram.com/ghalbe_daroon/reel/DcRbdTOsajM/", "acc": "@ghalbe_daroon", "views": "848K"},
        {"shortcode": "DdeT1ecMq7y", "url": "https://www.instagram.com/text.love400/reel/DdeT1ecMq7y/", "acc": "@text.love400", "views": "1.9M"},
        {"shortcode": "DdEeNFfs5V3", "url": "https://www.instagram.com/text.love400/reel/DdEeNFfs5V3/", "acc": "@text.love400", "views": "1.7M"},
    ]
    
    for c in cands:
        print(f"Inspecting {c['shortcode']} ({c['acc']} | {c['views']})...")
        await cdp.navigate(sid, c['url'])
        await asyncio.sleep(4.0)
        
        pause_js = """
        (() => {
            let v = document.querySelector('video');
            if (v) { v.currentTime = 2.0; v.pause(); }
        })()
        """
        await cdp.evaluate(sid, pause_js)
        await asyncio.sleep(1.0)
        
        fpath = os.path.join(frame_dir, f"{c['shortcode']}_frame.png")
        await cdp.capture_screenshot(sid, fpath)
        print(f"  Captured: {fpath}")
        
    await cdp.close()
    print("Done inspecting 5 cands!")

if __name__ == "__main__":
    asyncio.run(inspect_five())
