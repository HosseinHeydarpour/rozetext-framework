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

async def scan_profile(ws, session_id, profile_url, start_scroll=0, max_scrolls=30):
    print(f"\nNavigating to {profile_url}...")
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
        scroll_script = "window.scrollBy(0, 1200);"
        await ws.send(json.dumps({"id": 200 + i, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": scroll_script}}))
        await asyncio.sleep(1.2)
        
    return collected

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
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
        
        # 1. Scan ___yeharf
        yeharf_reels = await scan_profile(ws, session_id, "https://www.instagram.com/___yeharf/reels/", max_scrolls=20)
        print(f"Total yeharf reels: {len(yeharf_reels)}")
        yeharf_1m = []
        for c, (u, v) in yeharf_reels.items():
            if ("M" in v or "میلیون" in v) and not ("0." in v) and c not in existing_codes:
                yeharf_1m.append((c, v, u))
        print(f"Unused 1M+ yeharf: {len(yeharf_1m)}")
        for c, v, u in yeharf_1m:
            print(f" - {c}: {v} -> {u}")
            
        # 2. Deep scroll vahidrezakhoshbayan (scroll 35 times)
        khosh_reels = await scan_profile(ws, session_id, "https://www.instagram.com/vahidrezakhoshbayan/reels/", max_scrolls=35)
        print(f"\nTotal khoshbayan reels: {len(khosh_reels)}")
        khosh_1m = []
        for c, (u, v) in khosh_reels.items():
            if ("M" in v or "میلیون" in v) and not ("0." in v) and c not in existing_codes:
                khosh_1m.append((c, v, u))
        print(f"Unused 1M+ khoshbayan: {len(khosh_1m)}")
        for c, v, u in khosh_1m:
            print(f" - {c}: {v} -> {u}")

if __name__ == "__main__":
    asyncio.run(main())
