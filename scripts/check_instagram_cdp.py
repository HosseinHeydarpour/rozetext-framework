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
    
    async with websockets.connect(ws_url) as browser_ws:
        # Create a new tab for instagram
        msg = {
            "id": 1,
            "method": "Target.createTarget",
            "params": {"url": "https://www.instagram.com/"}
        }
        await browser_ws.send(json.dumps(msg))
        res = json.loads(await browser_ws.recv())
        target_id = res.get("result", {}).get("targetId")
        print(f"Created target: {target_id}")
        
        # Connect to this page target
        page_ws_url = f"ws://127.0.0.1:{port}/devtools/page/{target_id}"
        await asyncio.sleep(4)
        
        async with websockets.connect(page_ws_url) as page_ws:
            # Check document.title and URL
            eval_msg = {
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {"expression": "document.title + ' | ' + window.location.href"}
            }
            await page_ws.send(json.dumps(eval_msg))
            eval_res = json.loads(await page_ws.recv())
            print("Page info:", eval_res.get("result", {}).get("result", {}).get("value"))
            
            # Check if logged in by looking for login button or user profile link
            check_login = {
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": "document.body.innerText.slice(0, 300)"}
            }
            await page_ws.send(json.dumps(check_login))
            login_res = json.loads(await page_ws.recv())
            print("Body snippet:", login_res.get("result", {}).get("result", {}).get("value"))

if __name__ == "__main__":
    asyncio.run(main())
