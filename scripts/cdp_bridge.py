import asyncio
import json
import os
import sys
import websockets
from aiohttp import web
import urllib.request

# Ensure scripts dir is in path
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
from chrome_cdp import get_browser_ws

class PersistentCDPBridge:
    def __init__(self, port=9223):
        self.port = port
        self.ws = None
        self.msg_id = 0
        self.pending_futures = {} # cid -> Future
        self.sessions = {} # targetId -> sessionId
        self.is_connected = False
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/status', self.handle_health)
        self.app.router.add_post('/cmd', self.handle_cmd)
        self.app.router.add_get('/targets', self.handle_list_targets)
        self.app.router.add_post('/attach', self.handle_attach)
        self.app.router.add_post('/evaluate', self.handle_evaluate)
        self.app.router.add_post('/navigate', self.handle_navigate)
        self.app.router.add_post('/capture_screenshot', self.handle_capture_screenshot)

    async def connect_chrome(self):
        while True:
            try:
                ws_url = get_browser_ws()
                print(f"[CDP-BRIDGE] Connecting to Chrome CDP at: {ws_url} ...")
                print("[CDP-BRIDGE] >>> Please click 'ALLOW' in Chrome if a permission prompt appears! <<<")
                self.ws = await websockets.connect(ws_url, max_size=50 * 1024 * 1024, open_timeout=300)
                self.is_connected = True
                print("[CDP-BRIDGE] Successfully connected to Chrome! Single-session socket is now ACTIVE.")
                # Run receiver loop
                asyncio.create_task(self.receiver_loop())
                asyncio.create_task(self.keepalive_loop())
                break
            except Exception as e:
                print(f"[CDP-BRIDGE] Waiting for Chrome to be ready or user permission... ({e})")
                await asyncio.sleep(3)

    async def receiver_loop(self):
        while self.is_connected and self.ws:
            try:
                raw = await self.ws.recv()
                data = json.loads(raw)
                cid = data.get("id")
                if cid and cid in self.pending_futures:
                    fut = self.pending_futures.pop(cid)
                    if not fut.done():
                        fut.set_result(data)
            except Exception as e:
                print(f"[CDP-BRIDGE] Receiver loop disconnected: {e}")
                self.is_connected = False
                break

    async def keepalive_loop(self):
        while self.is_connected and self.ws:
            await asyncio.sleep(20)
            try:
                # Lightweight heartbeat
                await self.send_raw_cmd("Browser.getVersion")
            except Exception:
                pass

    async def send_raw_cmd(self, method, params=None, session_id=None, timeout=60):
        if not self.is_connected or not self.ws:
            raise ConnectionError("Bridge is not currently connected to Chrome.")
        
        self.msg_id += 1
        cid = self.msg_id
        payload = {"id": cid, "method": method}
        if params is not None:
            payload["params"] = params
        if session_id:
            payload["sessionId"] = session_id

        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self.pending_futures[cid] = fut

        await self.ws.send(json.dumps(payload))
        data = await asyncio.wait_for(fut, timeout=timeout)
        if "error" in data:
            raise RuntimeError(f"CDP Error in {method}: {data['error']}")
        return data.get("result", {})

    async def handle_health(self, request):
        return web.json_response({
            "status": "ok",
            "connected": self.is_connected,
            "port": self.port,
            "cached_sessions": len(self.sessions)
        })

    async def handle_cmd(self, request):
        try:
            body = await request.json()
            method = body.get("method")
            params = body.get("params")
            session_id = body.get("sessionId")
            result = await self.send_raw_cmd(method, params, session_id)
            return web.json_response({"result": result})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_list_targets(self, request):
        try:
            res = await self.send_raw_cmd("Target.getTargets")
            pages = [t for t in res.get("targetInfos", []) if t.get("type") == "page"]
            return web.json_response({"targets": pages})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_attach(self, request):
        try:
            body = await request.json()
            target_id = body.get("targetId")
            if target_id in self.sessions:
                return web.json_response({"sessionId": self.sessions[target_id]})
            res = await self.send_raw_cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True})
            session_id = res.get("sessionId")
            self.sessions[target_id] = session_id
            return web.json_response({"sessionId": session_id})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_evaluate(self, request):
        try:
            body = await request.json()
            session_id = body.get("sessionId")
            expression = body.get("expression")
            await_promise = body.get("awaitPromise", True)
            res = await self.send_raw_cmd("Runtime.evaluate", {
                "expression": expression,
                "awaitPromise": await_promise,
                "returnByValue": True
            }, session_id=session_id)
            if "exceptionDetails" in res:
                return web.json_response({"error": f"JS Exception: {res['exceptionDetails']}"}, status=400)
            return web.json_response({"value": res.get("result", {}).get("value")})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_navigate(self, request):
        try:
            body = await request.json()
            session_id = body.get("sessionId")
            url = body.get("url")
            res = await self.send_raw_cmd("Page.navigate", {"url": url}, session_id=session_id)
            return web.json_response({"result": res})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def handle_capture_screenshot(self, request):
        try:
            import base64
            body = await request.json()
            session_id = body.get("sessionId")
            output_path = body.get("output_path")
            res = await self.send_raw_cmd("Page.captureScreenshot", {"format": "png"}, session_id=session_id)
            img_data = base64.b64decode(res["data"])
            if output_path:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(img_data)
            return web.json_response({"output_path": output_path, "size": len(img_data)})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

async def main():
    bridge = PersistentCDPBridge(port=9223)
    runner = web.AppRunner(bridge.app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 9223)
    await site.start()
    print("[CDP-BRIDGE] HTTP Server listening on http://127.0.0.1:9223")
    
    # Connect to Chrome
    await bridge.connect_chrome()

    # Keep running forever
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[CDP-BRIDGE] Stopped by user.")
