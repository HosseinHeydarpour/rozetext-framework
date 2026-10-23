import asyncio
import json
import os
import sys
import websockets
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_URL = "http://127.0.0.1:9223"

def get_browser_ws(port: int = 9222) -> str:
    """Connect to Chrome CDP by checking DevToolsActivePort first, then HTTP /json/version fallback."""
    candidates = [
        os.path.expanduser(r"~/.chrome-hunter/DevToolsActivePort"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\User Data\DevToolsActivePort"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            try:
                with open(c, "r", encoding="utf-8") as f:
                    p = f.readline().strip()
                    path = f.readline().strip()
                if p and path:
                    return f"ws://127.0.0.1:{p}{path}"
            except Exception:
                pass

    for p in [port]:
        try:
            url = f"http://127.0.0.1:{p}/json/version"
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    ws = data.get("webSocketDebuggerUrl")
                    if ws:
                        return ws
        except Exception:
            pass

    raise ConnectionError("Chrome remote debugging is not reachable. Please start Chrome or ensure DevTools is active.")

class ChromeCDP:
    def __init__(self, bridge_url=BRIDGE_URL):
        self.bridge_url = bridge_url
        self.use_bridge = False
        self.ws = None
        self.msg_id = 0
        self.sessions = {} # targetId -> sessionId

    async def connect(self):
        # 1. Proactively check if persistent bridge daemon is active and connected
        try:
            req = urllib.request.Request(f"{self.bridge_url}/health")
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    if data.get("connected"):
                        self.use_bridge = True
                        return
        except Exception:
            pass

        # 2. Fallback to direct WebSocket connection to Chrome
        ws_url = get_browser_ws()
        self.ws = await websockets.connect(ws_url, max_size=50 * 1024 * 1024, open_timeout=60)

    async def close(self):
        if self.use_bridge:
            # Leave the persistent bridge connection alive for subsequent scripts!
            return
        if self.ws:
            await self.ws.close()

    async def send_cmd(self, method, params=None, session_id=None):
        if self.use_bridge:
            payload = json.dumps({"method": method, "params": params, "sessionId": session_id}).encode('utf-8')
            req = urllib.request.Request(f"{self.bridge_url}/cmd", data=payload, headers={"Content-Type": "application/json"})
            loop = asyncio.get_running_loop()
            def do_req():
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return json.loads(resp.read().decode())
            res = await loop.run_in_executor(None, do_req)
            if "error" in res:
                raise Exception(f"CDP Error in {method}: {res['error']}")
            return res.get("result", {})

        self.msg_id += 1
        cid = self.msg_id
        payload = {"id": cid, "method": method}
        if params is not None:
            payload["params"] = params
        if session_id:
            payload["sessionId"] = session_id
        await self.ws.send(json.dumps(payload))
        while True:
            raw = await self.ws.recv()
            data = json.loads(raw)
            if data.get("id") == cid:
                if "error" in data:
                    raise Exception(f"CDP Error in {method}: {data['error']}")
                return data.get("result", {})

    async def list_targets(self):
        if self.use_bridge:
            req = urllib.request.Request(f"{self.bridge_url}/targets")
            loop = asyncio.get_running_loop()
            def do_req():
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return json.loads(resp.read().decode())
            data = await loop.run_in_executor(None, do_req)
            return data.get("targets", [])
        res = await self.send_cmd("Target.getTargets")
        return [t for t in res.get("targetInfos", []) if t["type"] == "page"]

    async def attach_page(self, target_id):
        if target_id in self.sessions:
            return self.sessions[target_id]
        if self.use_bridge:
            payload = json.dumps({"targetId": target_id}).encode('utf-8')
            req = urllib.request.Request(f"{self.bridge_url}/attach", data=payload, headers={"Content-Type": "application/json"})
            loop = asyncio.get_running_loop()
            def do_req():
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return json.loads(resp.read().decode())
            data = await loop.run_in_executor(None, do_req)
            session_id = data.get("sessionId")
            self.sessions[target_id] = session_id
            return session_id
        res = await self.send_cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = res.get("sessionId")
        self.sessions[target_id] = session_id
        return session_id

    async def evaluate(self, session_id, expression, await_promise=True):
        if self.use_bridge:
            payload = json.dumps({
                "sessionId": session_id,
                "expression": expression,
                "awaitPromise": await_promise
            }).encode('utf-8')
            req = urllib.request.Request(f"{self.bridge_url}/evaluate", data=payload, headers={"Content-Type": "application/json"})
            loop = asyncio.get_running_loop()
            def do_req():
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return json.loads(resp.read().decode())
            data = await loop.run_in_executor(None, do_req)
            if "error" in data:
                raise Exception(f"JS Exception: {data['error']}")
            return data.get("value")
        res = await self.send_cmd("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": await_promise,
            "returnByValue": True
        }, session_id=session_id)
        if "exceptionDetails" in res:
            raise Exception(f"JS Exception: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    async def navigate(self, session_id, url):
        if self.use_bridge:
            payload = json.dumps({"sessionId": session_id, "url": url}).encode('utf-8')
            req = urllib.request.Request(f"{self.bridge_url}/navigate", data=payload, headers={"Content-Type": "application/json"})
            loop = asyncio.get_running_loop()
            def do_req():
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            return await loop.run_in_executor(None, do_req)
        return await self.send_cmd("Page.navigate", {"url": url}, session_id=session_id)

    async def capture_screenshot(self, session_id, output_path):
        if self.use_bridge:
            payload = json.dumps({"sessionId": session_id, "output_path": output_path}).encode('utf-8')
            req = urllib.request.Request(f"{self.bridge_url}/capture_screenshot", data=payload, headers={"Content-Type": "application/json"})
            loop = asyncio.get_running_loop()
            def do_req():
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read().decode())
            await loop.run_in_executor(None, do_req)
            return output_path
        import base64
        res = await self.send_cmd("Page.captureScreenshot", {"format": "png"}, session_id=session_id)
        img_data = base64.b64decode(res["data"])
        with open(output_path, "wb") as f:
            f.write(img_data)
        return output_path
