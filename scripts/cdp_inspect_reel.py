import asyncio
import json
import os
import sys
import base64
import websockets

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES_DIR = os.path.join(BASE_DIR, "downloads", "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

candidate_codes = [
    ("DcDeSnws_Yq", "1.9M"),
    ("DbGUEgZsr6E", "5.3M"),
    ("Da7s8a7slWn", "4.0M"),
    ("DakLbcdMUof", "1.6M"),
    ("DacgLbesHkB", "5.5M"),
    ("Da2YyLdsQMo", "1.5M")
]

async def inspect_reel(ws, session_id, code, views):
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"\n==========================================")
    print(f"Navigating to {url} ({views})...")
    print(f"==========================================")
    
    # Navigate
    await ws.send(json.dumps({"id": 10, "sessionId": session_id, "method": "Page.navigate", "params": {"url": url}}))
    await asyncio.sleep(4.5)
    
    # Extract text from video and description
    prep_script = """
    (() => {
        const video = document.querySelector('video');
        let videoData = { found: false };
        if (video) {
            video.pause();
            video.currentTime = 2.0;
            const rect = video.getBoundingClientRect();
            videoData = {
                found: true,
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                duration: video.duration
            };
        }
        
        // Find text content on page
        const textElements = Array.from(document.querySelectorAll('h1, h2, span, div'))
            .map(el => el.innerText ? el.innerText.trim() : '')
            .filter(t => t.length > 20 && !t.includes('Instagram') && !t.includes('Meta'));
            
        return {
            video: videoData,
            title: document.title,
            url: window.location.href,
            bodySnippet: document.body ? document.body.innerText.slice(0, 1000) : ''
        };
    })()
    """
    await ws.send(json.dumps({"id": 20, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": prep_script, "returnByValue": True}}))
    
    page_info = {}
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == 20:
            page_info = msg.get("result", {}).get("result", {}).get("value", {})
            break
            
    print("Page Title / URL:", page_info.get("title"), "|", page_info.get("url"))
    print("Body snippet:\n", page_info.get("bodySnippet")[:300])
    
    video_info = page_info.get("video", {})
    clip_param = None
    if video_info.get("found") and video_info.get("width") > 0:
        clip_param = {
            "x": max(0, video_info["x"]),
            "y": max(0, video_info["y"]),
            "width": video_info["width"],
            "height": video_info["height"],
            "scale": 1
        }
        
    shot_params = {"format": "png"}
    if clip_param:
        shot_params["clip"] = clip_param
        
    await ws.send(json.dumps({"id": 30, "sessionId": session_id, "method": "Page.captureScreenshot", "params": shot_params}))
    
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == 30:
            data = msg.get("result", {}).get("data", "")
            if data:
                img_bytes = base64.b64decode(data)
                out_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print(f"SAVED SCREENSHOT: {out_path} ({len(img_bytes)} bytes)")
            break

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=50*1024*1024, origin=None) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "instagram" in t.get("url", ""):
                target_id = t["targetId"]
                break
                
        if not target_id:
            print("No Instagram target found among targets!")
            return
            
        await ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": target_id, "flatten": True}}))
        session_id = None
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 2:
                session_id = msg.get("result", {}).get("sessionId")
                break
            elif msg.get("method") == "Target.attachedToTarget":
                session_id = msg.get("params", {}).get("sessionId")
                break
                
        print(f"Attached session: {session_id}")
        
        # Test first 2 candidates: DcDeSnws_Yq (1.9M) and DbGUEgZsr6E (5.3M)
        for code, views in candidate_codes[:3]:
            await inspect_reel(ws, session_id, code, views)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
