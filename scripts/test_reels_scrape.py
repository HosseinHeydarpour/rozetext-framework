import asyncio
import json
import os
import sys
import websockets

sys.stdout.reconfigure(encoding='utf-8')

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
                
        print(f"Attached: {session_id}")
        
        # Navigate to a target url
        target_page = "https://www.instagram.com/vahidrezakhoshbayan/reels/"
        print(f"Navigating to {target_page}...")
        
        nav_msg = {
            "id": 10,
            "sessionId": session_id,
            "method": "Page.navigate",
            "params": {"url": target_page}
        }
        await ws.send(json.dumps(nav_msg))
        
        # Wait a few seconds for navigation and content load
        await asyncio.sleep(6)
        
        # Extract reels with play counts
        extract_script = """
        (() => {
            const reels = [];
            const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
            for (const a of links) {
                const href = a.href;
                // find view count in text or innerText
                const text = a.innerText.trim();
                reels.push({
                    url: href,
                    text: text
                });
            }
            return {
                title: document.title,
                count: reels.length,
                reels: reels.slice(0, 30)
            };
        })()
        """
        
        await ws.send(json.dumps({
            "id": 20,
            "sessionId": session_id,
            "method": "Runtime.evaluate",
            "params": {"expression": extract_script, "returnByValue": True}
        }))
        
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 20:
                val = msg.get("result", {}).get("result", {}).get("value")
                print("Extracted reels count:", val.get("count"))
                for r in val.get("reels", []):
                    print("  ", r["url"], "->", repr(r["text"]))
                break

if __name__ == "__main__":
    asyncio.run(main())
