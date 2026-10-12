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
        res = json.loads(await ws.recv())
        targets = res.get("result", {}).get("targetInfos", [])
        print(f"Total targets: {len(targets)}")
        for t in targets:
            if t.get("type") == "page":
                print(f"PAGE: {t.get('targetId')} | {t.get('title')} | {t.get('url')}")

if __name__ == "__main__":
    asyncio.run(main())
