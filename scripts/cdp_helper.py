import asyncio
import json
import os
import sys
import websockets

def get_browser_ws():
    local_appdata = os.environ.get("LOCALAPPDATA")
    port_file = os.path.join(local_appdata, r"Google\Chrome\User Data\DevToolsActivePort")
    with open(port_file, "r") as f:
        port = f.readline().strip()
        path = f.readline().strip()
    return f"ws://127.0.0.1:{port}{path}"

async def list_tabs():
    ws_url = get_browser_ws()
    async with websockets.connect(ws_url) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        res = await ws.recv()
        targets = json.loads(res)["result"]["targetInfos"]
        pages = [t for t in targets if t["type"] == "page"]
        return pages

if __name__ == "__main__":
    pages = asyncio.run(list_tabs())
    for p in pages:
        print(f"{p['targetId']} | {p['title'][:40]} | {p['url']}")
