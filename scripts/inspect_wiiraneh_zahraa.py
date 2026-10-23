import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def inspect_batch():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("[!] No IG tab")
        return
        
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    urls = [
        ("https://www.instagram.com/wiiraneh/reel/DbzHnCos0va/", "1.7M", "@wiiraneh"),
        ("https://www.instagram.com/wiiraneh/reel/Dbj1MxAIZPI/", "1.2M", "@wiiraneh"),
        ("https://www.instagram.com/wiiraneh/reel/Dbd-li8tY46/", "927K", "@wiiraneh"),
        ("https://www.instagram.com/zahraa.nature/reel/DcbwxDxPMvY/", "1.7M", "@zahraa.nature"),
        ("https://www.instagram.com/zahraa.nature/reel/Db1UjoWMV8Q/", "1.6M", "@zahraa.nature"),
        ("https://www.instagram.com/zahraa.nature/reel/DcRrYXESCEI/", "1.1M", "@zahraa.nature"),
    ]

    for idx, (url, v, acc) in enumerate(urls, 1):
        shortcode = url.strip('/').split('/')[-1]
        print(f"[{idx}/{len(urls)}] Inspecting {url} ({v} - {acc})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)

        # Pause at second 2
        pause_js = """
        (() => {
            let v = document.querySelector('video');
            if (v) {
                v.currentTime = 2.0;
                v.pause();
            }
        })()
        """
        await cdp.evaluate(sid, pause_js)
        await asyncio.sleep(1.0)

        frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
        frame_path = os.path.join(frame_dir, f"{shortcode}_frame.png")
        await cdp.capture_screenshot(sid, frame_path)
        print(f"   [+] Frame: {frame_path}")

    await cdp.close()

if __name__ == "__main__":
    asyncio.run(inspect_batch())
