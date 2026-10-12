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
    
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        # Get all targets
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "instagram" in t.get("url", ""):
                target_id = t["targetId"]
                print(f"Target: {t['targetId']} | {t.get('url')} | {t.get('title')}")
                break
                
        # Attach to target
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
                
        print(f"Got sessionId: {session_id}")
        
        # Now evaluate on that page
        eval_script = """
        (() => {
            const username = document.querySelector('header section h2, header h2, a[href*="/direct/"]')?.innerText || 'unknown';
            return {
                title: document.title,
                url: window.location.href,
                bodyText: document.body ? document.body.innerText.slice(0, 500) : '',
                htmlSnippet: document.body ? document.body.innerHTML.slice(0, 500) : ''
            };
        })()
        """
        
        await ws.send(json.dumps({
            "id": 10,
            "sessionId": session_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": eval_script,
                "returnByValue": True
            }
        }))
        
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 10:
                print("EVAL RESULT:")
                res = msg.get("result", {}).get("result", {}).get("value")
                print(json.dumps(res, indent=2, ensure_ascii=False))
                break

if __name__ == "__main__":
    asyncio.run(main())
