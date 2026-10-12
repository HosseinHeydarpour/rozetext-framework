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

test_candidates = [
    ("DIKL9gZqM6_", "2.5M", "@texthayedeli.ir"),
    ("DXB0KDZIF1S", "2.2M", "@be_yar"),
    ("DJRtdV1oHYS", "2.8M", "@parvaa_edit"),
    ("C_8r9QeuqGO", "1.8M", "@harfamine"),
    ("DUGn15ajilB", "2.0M", "@tan___ha28a"),
    ("DSOdHfCiOYd", "2.3M", "@itrephe"),
    ("DUtC3ynjJUp", "1.9M", "@leyli_geraphy")
]

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=25*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "EC0B4236635E918AC4B1C440773F5D7B" == t.get("targetId") or "(9+)" in t.get("title", ""):
                target_id = t["targetId"]
                break
                
        if not target_id:
            print("Could not find logged-in target!")
            return
            
        print(f"Attaching to target: {target_id}")
        await ws.send(json.dumps({
            "id": 2,
            "method": "Target.attachToTarget",
            "params": {"targetId": target_id, "flatten": True}
        }))
        
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
        
        req_id = 100
        for code, views, page in test_candidates:
            url = f"https://www.instagram.com/reel/{code}/"
            print(f"\n==========================================")
            print(f"Navigating to {url} ({views} - {page})...")
            print(f"==========================================")
            
            # Navigate using location.href or Page.navigate
            await ws.send(json.dumps({
                "id": req_id,
                "sessionId": session_id,
                "method": "Page.navigate",
                "params": {"url": url}
            }))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == req_id:
                    break
            req_id += 1
            
            # Wait for video and layout to load
            await asyncio.sleep(6.0)
            
            # Evaluate script to pause video and get metadata
            prep_script = """
            (() => {
                const video = document.querySelector('video');
                let vidData = { found: false };
                if (video) {
                    try {
                        video.pause();
                        video.currentTime = 2.5;
                    } catch(e) {}
                    const rect = video.getBoundingClientRect();
                    vidData = {
                        found: true,
                        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                        duration: video.duration
                    };
                }
                
                // Get all visible text snippets on the page
                const texts = Array.from(document.querySelectorAll('h1, h2, span, div, p'))
                    .map(el => (el.innerText || '').trim())
                    .filter(t => t.length > 15 && !t.includes('Instagram') && !t.includes('Meta'));
                    
                return {
                    title: document.title,
                    url: window.location.href,
                    video: vidData,
                    texts: texts.slice(0, 10),
                    bodySnippet: document.body ? document.body.innerText.slice(0, 1000) : ''
                };
            })()
            """
            await ws.send(json.dumps({
                "id": req_id,
                "sessionId": session_id,
                "method": "Runtime.evaluate",
                "params": {"expression": prep_script, "returnByValue": True}
            }))
            
            page_data = {}
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == req_id:
                    page_data = msg.get("result", {}).get("result", {}).get("value", {})
                    break
            req_id += 1
            
            print("Title:", page_data.get("title"))
            print("URL:", page_data.get("url"))
            print("Video found:", page_data.get("video", {}).get("found"))
            print("Body snippet:\n", page_data.get("bodySnippet", "")[:300])
            
            # Screenshot the whole page or video
            shot_params = {"format": "png"}
            await ws.send(json.dumps({
                "id": req_id,
                "sessionId": session_id,
                "method": "Page.captureScreenshot",
                "params": shot_params
            }))
            
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == req_id:
                    data = msg.get("result", {}).get("data", "")
                    if data:
                        img_bytes = base64.b64decode(data)
                        out_path = os.path.join(FRAMES_DIR, f"{code}_logged_frame.png")
                        with open(out_path, "wb") as f:
                            f.write(img_bytes)
                        print(f"--> SAVED LOGGED SCREENSHOT: {out_path} ({len(img_bytes)/1024:.1f} KB)")
                    break
            req_id += 1
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    asyncio.run(main())
