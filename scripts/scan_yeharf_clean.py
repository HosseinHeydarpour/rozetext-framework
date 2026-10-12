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

already_verified_9 = {
    "DNtMbWm0P4y", "DNTYt15oqYj", "DZDRxCkNgjw", "DbQ5ACmslaO", 
    "DPjl0mTCIps", "DO_homTiPTp", "DMqPqQCIem7", "DbyY0F7tmAn", "DPRj9ddCF5T"
}

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    
    async with websockets.connect(ws_url, max_size=50*1024*1024, open_timeout=15) as ws:
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
        
        # Navigate to https://www.instagram.com/___yeharf/reels/
        print("Navigating to https://www.instagram.com/___yeharf/reels/ ...")
        await ws.send(json.dumps({"id": 10, "sessionId": session_id, "method": "Page.navigate", "params": {"url": "https://www.instagram.com/___yeharf/reels/"}}))
        await asyncio.sleep(6)
        
        reels_map = {}
        for s in range(12):
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
            await ws.send(json.dumps({"id": 100 + s, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": extract_script, "returnByValue": True}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 100 + s:
                    items = msg.get("result", {}).get("result", {}).get("value", [])
                    for it in items:
                        u = it["url"]
                        code = u.strip().rstrip("/").split("/")[-1]
                        txt = it["text"]
                        if code not in reels_map and txt:
                            reels_map[code] = (u, txt)
                    break
            await ws.send(json.dumps({"id": 200 + s, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": "window.scrollBy(0, 1000);"}}))
            await asyncio.sleep(1.2)
            
        print(f"Total yeharf reels collected: {len(reels_map)}")
        for c, (u, v) in reels_map.items():
            if ("M" in v or "میلیون" in v) and not ("0." in v):
                in_db = c in existing_codes
                print(f"Yeharf 1M+: {c} | {v} | in_db={in_db} | {u}")

if __name__ == "__main__":
    asyncio.run(main())
