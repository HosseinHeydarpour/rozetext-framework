import urllib.request
import json
import sys

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
s = res.get("sessionId")

import base64
cmd_data = {
    "method": "Page.captureScreenshot",
    "params": {"format": "png"},
    "sessionId": s
}
ss_res = post("/cmd", cmd_data)
b64 = ss_res.get("result", {}).get("data")
if b64:
    with open("downloads/current_screen.png", "wb") as f:
        f.write(base64.b64decode(b64))
    print("Screenshot saved to downloads/current_screen.png")
