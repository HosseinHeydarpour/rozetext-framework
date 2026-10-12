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

async def inspect_reel(ws, session_id, code, views, req_id_base):
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"\n==========================================")
    print(f"Navigating to {url} ({views})...")
    print(f"==========================================")
    
    # Navigate
    await ws.send(json.dumps({
        "id": req_id_base + 1,
        "sessionId": session_id,
        "method": "Page.navigate",
        "params": {"url": url}
    }))
    
    # Wait for response and page load
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == req_id_base + 1:
            break
            
    await asyncio.sleep(5.0)
    
    # Pause video and extract info
    prep_script = """
    (() => {
        const video = document.querySelector('video');
        let videoData = { found: false };
        if (video) {
            try {
                video.pause();
                video.currentTime = 2.0;
            } catch(e) {}
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
        
        // Find main post text
        let caption = '';
        const captionH1 = document.querySelector('h1');
        if (captionH1) caption = captionH1.innerText;
        
        return {
            video: videoData,
            title: document.title,
            caption: caption,
            bodySnippet: document.body ? document.body.innerText.slice(0, 1500) : ''
        };
    })()
    """
    await ws.send(json.dumps({
        "id": req_id_base + 2,
        "sessionId": session_id,
        "method": "Runtime.evaluate",
        "params": {"expression": prep_script, "returnByValue": True}
    }))
    
    page_info = {}
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == req_id_base + 2:
            page_info = msg.get("result", {}).get("result", {}).get("value", {})
            break
            
    print("Page Title:", page_info.get("title"))
    print("Caption snippet:", repr(page_info.get("caption", ""))[:200])
    
    # Capture Screenshot
    # First try video clip if valid, otherwise full page
    v = page_info.get("video", {})
    shot_params = {"format": "png"}
    if v.get("found") and v.get("width", 0) > 100 and v.get("height", 0) > 100:
        shot_params["clip"] = {
            "x": max(0, v["x"]),
            "y": max(0, v["y"]),
            "width": v["width"],
            "height": v["height"],
            "scale": 1
        }
    
    await ws.send(json.dumps({
        "id": req_id_base + 3,
        "sessionId": session_id,
        "method": "Page.captureScreenshot",
        "params": shot_params
    }))
    
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == req_id_base + 3:
            data = msg.get("result", {}).get("data", "")
            if data:
                img_bytes = base64.b64decode(data)
                out_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print(f"--> SAVED SCREENSHOT: {out_path} ({len(img_bytes)/1024:.1f} KB)")
            break

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
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
        
        req_base = 100
        for code, views in candidate_codes:
            try:
                await inspect_reel(ws, session_id, code, views, req_base)
            except Exception as e:
                print(f"Error inspecting {code}: {e}")
            req_base += 10
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
