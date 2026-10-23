import asyncio
import json
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine
from rozetext_scoring_engine_v3 import evaluate_script_v3

engine = AntiDuplicationEngine.get_instance()

async def inspect_reels(urls):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("[!] No IG tab found")
        return []
    
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    results = []

    for idx, (url, expected_views, page_name) in enumerate(urls, 1):
        shortcode = url.strip('/').split('/')[-1]
        print(f"\n[{idx}/{len(urls)}] Inspecting {url} ({expected_views} views - {page_name})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)

        # Pause video at second 2
        pause_js = """
        (() => {
            let v = document.querySelector('video');
            if (v) {
                v.currentTime = 2.0;
                v.pause();
                return { duration: v.duration, currentTime: v.currentTime };
            }
            return null;
        })()
        """
        v_meta = await cdp.evaluate(sid, pause_js)
        await asyncio.sleep(1.0)

        # Capture frame
        frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
        os.makedirs(frame_dir, exist_ok=True)
        frame_path = os.path.join(frame_dir, f"{shortcode}_frame.png")
        await cdp.capture_screenshot(sid, frame_path)
        print(f"   [+] Frame captured: {frame_path}")

        # Extract text elements from page
        extract_js = """
        (() => {
            let spans = Array.from(document.querySelectorAll('article span, main span, h1, div[dir="auto"]'))
                .map(s => s.innerText.trim())
                .filter(t => t.length > 3 && !t.includes('Follow') && !t.includes('دنبال'));
            
            let h1 = document.querySelector('h1');
            let caption = h1 ? h1.innerText : '';

            return {
                spans: spans.slice(0, 40),
                caption: caption
            };
        })()
        """
        dom_data = await cdp.evaluate(sid, extract_js) or {}
        results.append({
            "url": url,
            "shortcode": shortcode,
            "expected_views": expected_views,
            "page_name": page_name,
            "frame_path": frame_path,
            "dom_data": dom_data
        })

    await cdp.close()
    return results

if __name__ == "__main__":
    test_urls = [
        ("https://www.instagram.com/reel/DcGUbIrt1Yc/", "4.2M", "@leyli_geraphy"),
        ("https://www.instagram.com/reel/DdRpP_vo6P2/", "3.9M", "@matne_ziba"),
        ("https://www.instagram.com/reel/DdcA1OVC3dg/", "2.0M", "@___yeharf"),
        ("https://www.instagram.com/reel/DcDeSnws_Yq/", "2.0M", "@text.love400"),
        ("https://www.instagram.com/reel/DdeT1ecMq7y/", "1.8M", "@text.love400"),
        ("https://www.instagram.com/reel/Ddmz-WgRM4K/", "1.6M", "@___yeharf"),
    ]
    asyncio.run(inspect_reels(test_urls))
