import asyncio
import json
import os
import sys
import base64
import websockets

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")
FRAMES_DIR = os.path.join(BASE_DIR, "downloads", "frames")

with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

existing_codes = set()
for s in db.get("scripts", []):
    u = s.get("source_url", "")
    if u:
        code = u.strip().rstrip("/").split("/")[-1]
        existing_codes.add(code)

# Add our 9 already verified
already_used = {
    "DNtMbWm0P4y", "DNTYt15oqYj", "DZDRxCkNgjw", "DbQ5ACmslaO", 
    "DPjl0mTCIps", "DO_homTiPTp", "DMqPqQCIem7", "DbyY0F7tmAn", "DPRj9ddCF5T"
}
existing_codes.update(already_used)

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    
    async with websockets.connect(ws_url, max_size=50*1024*1024, open_timeout=30) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "instagram" in t.get("url", ""):
                target_id = t["targetId"]
                break
                
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
        
        # 1. Let's inspect DKm6Qn6I9vQ at 4.0s
        print("\nInspecting DKm6Qn6I9vQ at 4.0s...")
        await ws.send(json.dumps({"id": 10, "sessionId": session_id, "method": "Page.navigate", "params": {"url": "https://www.instagram.com/reel/DKm6Qn6I9vQ/"}}))
        await asyncio.sleep(4)
        
        seek_script = """
        (() => {
            const video = document.querySelector('video');
            if (video) {
                video.pause();
                video.currentTime = 4.0;
                return {found: true, time: video.currentTime};
            }
            return {found: false};
        })()
        """
        await ws.send(json.dumps({"id": 11, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": seek_script, "returnByValue": True}}))
        await asyncio.sleep(1)
        
        await ws.send(json.dumps({"id": 12, "sessionId": session_id, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 12:
                data = msg.get("result", {}).get("data", "")
                with open(os.path.join(FRAMES_DIR, "DKm6Qn6I9vQ_frame4s.png"), "wb") as f:
                    f.write(base64.b64decode(data))
                print("Saved DKm6Qn6I9vQ_frame4s.png")
                break

        # 2. Go to https://www.instagram.com/___yeharf/reels/
        print("\nNavigating to https://www.instagram.com/___yeharf/reels/ ...")
        await ws.send(json.dumps({"id": 20, "sessionId": session_id, "method": "Page.navigate", "params": {"url": "https://www.instagram.com/___yeharf/reels/"}}))
        await asyncio.sleep(5)
        
        collected_yeharf = {}
        for i in range(15):
            extract_script = """
            (() => {
                const items = [];
                const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                for (const a of links) {
                    items.push({url: a.href, text: a.innerText.trim()});
                }
                return items;
            })()
            """
            await ws.send(json.dumps({"id": 100 + i, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": extract_script, "returnByValue": True}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 100 + i:
                    items = msg.get("result", {}).get("result", {}).get("value", [])
                    for it in items:
                        u = it["url"]
                        code = u.strip().rstrip("/").split("/")[-1]
                        txt = it["text"]
                        if code not in collected_yeharf and txt:
                            collected_yeharf[code] = (u, txt)
                    break
            scroll_script = "window.scrollBy(0, 1000);"
            await ws.send(json.dumps({"id": 200 + i, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": scroll_script}}))
            await asyncio.sleep(1.2)
            
        print(f"Total yeharf reels collected: {len(collected_yeharf)}")
        for c, (u, v) in collected_yeharf.items():
            if ("M" in v or "میلیون" in v) and not ("0." in v) and c not in existing_codes:
                print(f"Candidate Yeharf: {c} | {v} | {u}")

if __name__ == "__main__":
    asyncio.run(main())
