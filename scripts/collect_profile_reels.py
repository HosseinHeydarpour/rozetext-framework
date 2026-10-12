import asyncio
import json
import os
import sys
import websockets

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")

with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

existing_codes = set()
for s in db.get("scripts", []):
    u = s.get("source_url", "")
    if u:
        code = u.strip().rstrip("/").split("/")[-1]
        existing_codes.add(code)

print(f"Existing DB codes: {len(existing_codes)}")

async def scroll_and_collect(profile_url, max_scrolls=20):
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
        
        # Navigate
        print(f"Navigating to {profile_url}...")
        await ws.send(json.dumps({"id": 10, "sessionId": session_id, "method": "Page.navigate", "params": {"url": profile_url}}))
        await asyncio.sleep(5)
        
        collected = {}
        
        for i in range(max_scrolls):
            # Extract links and view text
            extract_script = """
            (() => {
                const items = [];
                const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                for (const a of links) {
                    const href = a.href;
                    const text = a.innerText.trim();
                    items.push({url: href, text: text});
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
                        if code not in collected and txt:
                            collected[code] = (u, txt)
                    break
                    
            # Scroll down
            scroll_script = "window.scrollBy(0, 1000);"
            await ws.send(json.dumps({"id": 200 + i, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": scroll_script}}))
            await asyncio.sleep(1.5)
            
        return collected

async def main():
    profiles = [
        "https://www.instagram.com/heliumm.__/reels/",
        "https://www.instagram.com/___yeharf/reels/"
    ]
    for p in profiles:
        print(f"\n--- Scanning {p} ---")
        reels = await scroll_and_collect(p, max_scrolls=20)
        print(f"Total reels collected: {len(reels)}")
        
        candidates = []
        for code, (url, view_text) in reels.items():
            is_m = ("M" in view_text or "میلیون" in view_text) and not ("0." in view_text)
            is_unused = code not in existing_codes
            if is_m and is_unused:
                candidates.append((code, view_text, url))
                
        print(f"Unused 1M+ candidates: {len(candidates)}")
        for c, v, u in candidates:
            print(f" - {c}: {v} -> {u}")

if __name__ == "__main__":
    asyncio.run(main())

