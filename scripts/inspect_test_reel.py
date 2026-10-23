import asyncio
import sys, os, json, base64
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

async def inspect_reel_test():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    url = "https://www.instagram.com/reel/DcGUbIrt1Yc/"
    print(f"Navigating to {url} ...")
    await cdp.navigate(sid, url)
    await asyncio.sleep(4)
    
    # Check video and take screenshot of video
    script = """
    (() => {
        let v = document.querySelector('video');
        if (!v) return {found: false};
        v.pause();
        v.currentTime = 2.0;
        let rect = v.getBoundingClientRect();
        return {
            found: true,
            duration: v.duration,
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height
        };
    })()
    """
    info = await cdp.evaluate(sid, script)
    print("Video info:", info)
    
    # Take screenshot of page
    ss_cmd = {
        "format": "png",
        "clip": {
            "x": max(0, info["x"]),
            "y": max(0, info["y"]),
            "width": max(100, info["width"]),
            "height": max(100, info["height"]),
            "scale": 1
        }
    } if info.get("found") else {"format": "png"}
    
    res = await cdp.send_cmd("Page.captureScreenshot", ss_cmd, session_id=sid)
    img_data = base64.b64decode(res["data"])
    os.makedirs("downloads/frames", exist_ok=True)
    out_path = "downloads/frames/DcGUbIrt1Yc_test.png"
    with open(out_path, "wb") as f:
        f.write(img_data)
    print(f"Saved screenshot to {out_path} ({len(img_data)} bytes)")
    
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(inspect_reel_test())
