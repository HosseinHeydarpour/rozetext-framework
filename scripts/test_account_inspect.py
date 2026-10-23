import asyncio
import json
import os
import sys
import websockets

async def check():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=10*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        res = json.loads(await ws.recv())
        targets = res.get("result", {}).get("targetInfos", [])
        ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
        if not ig_targets:
            print("No IG target")
            return
        
        target = ig_targets[0]
        await ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": target["targetId"], "flatten": True}}))
        res2 = json.loads(await ws.recv())
        sid = res2.get("params", {}).get("sessionId")
        
        js = """
        (() => {
            let res = {};
            let scripts = Array.from(document.querySelectorAll('script'));
            for (let s of scripts) {
                let txt = s.innerText || '';
                let idx = txt.indexOf('"username":"mimansa_wear"');
                if (idx !== -1) {
                    res.snippet = txt.substring(Math.max(0, idx - 100), Math.min(txt.length, idx + 400));
                    break;
                }
            }
            return res;
        })()
        """
        await ws.send(json.dumps({"id": 3, "sessionId": sid, "method": "Runtime.evaluate", "params": {"expression": js, "awaitPromise": False, "returnByValue": True}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 3:
                val = msg.get("result", {}).get("result", {}).get("value")
                print(json.dumps(val, ensure_ascii=False, indent=2))
                break

if __name__ == "__main__":
    asyncio.run(check())
