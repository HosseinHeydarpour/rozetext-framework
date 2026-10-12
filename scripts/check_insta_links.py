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
    
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        # Get all targets
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "instagram" in t.get("url", ""):
                target_id = t["targetId"]
                break
                
        if not target_id:
            # create target
            await ws.send(json.dumps({"id": 2, "method": "Target.createTarget", "params": {"url": "https://www.instagram.com/"}}))
            res = json.loads(await ws.recv())
            target_id = res["result"]["targetId"]
            await asyncio.sleep(2)
            
        # Attach to target
        await ws.send(json.dumps({"id": 3, "method": "Target.attachToTarget", "params": {"targetId": target_id, "flatten": True}}))
        session_id = None
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 3:
                session_id = msg.get("result", {}).get("sessionId")
                break
            elif msg.get("method") == "Target.attachedToTarget":
                session_id = msg.get("params", {}).get("sessionId")
                break

        print(f"Attached with sessionId: {session_id}")
        
        # Navigate to following or check feed
        # Let's see what is on current page
        eval_script = """
        (() => {
            const links = Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
            return {
                url: window.location.href,
                links: links.filter(l => l.includes('instagram.com')).slice(0, 30)
            };
        })()
        """
        await ws.send(json.dumps({
            "id": 4,
            "sessionId": session_id,
            "method": "Runtime.evaluate",
            "params": {"expression": eval_script, "returnByValue": True}
        }))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 4:
                print("Result:", msg.get("result", {}).get("result", {}).get("value"))
                break

if __name__ == "__main__":
    asyncio.run(main())
