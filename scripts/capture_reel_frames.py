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
    ("DNtMbWm0P4y", "2.2M"),
    ("DbbPmLFNZbj", "1.8M"),
    ("DNTYt15oqYj", "1.6M"),
    ("DZDRxCkNgjw", "1.5M"),
    ("DbQ5ACmslaO", "1.3M"),
    ("DKm6Qn6I9vQ", "1.3M"),
    ("DPjl0mTCIps", "1.2M"),
    ("DPeaox9CPJk", "1.2M"),
    ("DO_homTiPTp", "1.2M"),
    ("DMqPqQCIem7", "1.2M"),
    ("DbyY0F7tmAn", "1.1M"),
    ("DQHm9z6CMeL", "1.0M"),
    ("DPRj9ddCF5T", "1.0M")
]

async def inspect_reel(ws, session_id, code, views):
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"\nNavigating to {url} ({views})...")
    
    # Navigate
    await ws.send(json.dumps({"id": 10, "sessionId": session_id, "method": "Page.navigate", "params": {"url": url}}))
    await asyncio.sleep(4)
    
    # Pause video and get exact video dimensions/box
    prep_script = """
    (() => {
        const video = document.querySelector('video');
        if (video) {
            video.pause();
            video.currentTime = 2.0;
            const rect = video.getBoundingClientRect();
            return {
                found: true,
                currentTime: video.currentTime,
                duration: video.duration,
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                src: video.src
            };
        }
        return {found: false};
    })()
    """
    await ws.send(json.dumps({"id": 20, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": prep_script, "returnByValue": True}}))
    
    video_info = {}
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == 20:
            video_info = msg.get("result", {}).get("result", {}).get("value", {})
            break
            
    print("Video info:", video_info)
    await asyncio.sleep(1)
    
    # Capture screenshot of viewport or video
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
            img_bytes = base64.b64decode(data)
            out_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            print(f"Saved screenshot: {out_path} ({len(img_bytes)} bytes)")
            break

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        # Get targets
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "instagram" in t.get("url", ""):
                target_id = t["targetId"]
                break
                
        # Attach
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
        
        # Capture remaining candidates
        remaining = candidate_codes[4:]
        for code, views in remaining:
            await inspect_reel(ws, session_id, code, views)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

