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
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets_res = json.loads(await ws.recv())
        targets = targets_res.get("result", {}).get("targetInfos", [])
        
        target_id = None
        for t in targets:
            if "EC0B4236635E918AC4B1C440773F5D7B" == t.get("targetId") or "(9+)" in t.get("title", ""):
                target_id = t["targetId"]
                print(f"Found Logged-in Target: {t['targetId']} | {t.get('title')} | {t.get('url')}")
                break
                
        if not target_id:
            for t in targets:
                if "instagram.com" in t.get("url", "") and t.get("targetId") != "E4C1FB3F315B268274FEFEEC01E4AAE0":
                    target_id = t["targetId"]
                    print(f"Fallback Target: {t['targetId']} | {t.get('title')} | {t.get('url')}")
                    break

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
        
        # Check current user / login info
        eval_script = """
        (() => {
            return {
                title: document.title,
                url: window.location.href,
                cookiesLength: document.cookie.length,
                hasNav: !!document.querySelector('nav, [role="navigation"]'),
                bodyText: document.body ? document.body.innerText.slice(0, 300) : ''
            };
        })()
        """
        await ws.send(json.dumps({
            "id": 10,
            "sessionId": session_id,
            "method": "Runtime.evaluate",
            "params": {"expression": eval_script, "returnByValue": True}
        }))
        
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 10:
                res = msg.get("result", {}).get("result", {}).get("value")
                print("EVAL RESULT:\n", json.dumps(res, indent=2, ensure_ascii=False))
                break

if __name__ == "__main__":
    asyncio.run(main())
