import asyncio
import json
import os
import sys
import websockets

sys.stdout.reconfigure(encoding='utf-8')


async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    if not os.path.exists(port_file):
        print("DevToolsActivePort not found")
        return
        
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
        
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    print(f"Connecting to browser CDP: {ws_url}")
    
    async with websockets.connect(ws_url) as ws:
        # Get targets
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        res = json.loads(await ws.recv())
        targets = res.get("result", {}).get("targetInfos", [])
        print(f"Total targets: {len(targets)}")
        
        for t in targets:
            print(f"{t.get('type')}: {t.get('url')} | {t.get('title')}")

if __name__ == "__main__":
    asyncio.run(main())
