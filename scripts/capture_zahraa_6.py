import urllib.request
import json
import time
import base64
import os

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"
FRAMES_DIR = "downloads/frames"
os.makedirs(FRAMES_DIR, exist_ok=True)

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
session_id = res.get("sessionId")
print(f"Attached. Session: {session_id}")

cands = [
    ("DZhMLXHsw2v", "5.5M", "@zahraa.nature"),
    ("DYhyAZUMMOl", "1.2M", "@zahraa.nature"),
    ("DRkgE8vDzC4", "1M", "@zahraa.nature"),
    ("DZUgl9tMyzD", "814K", "@zahraa.nature"),
    ("Daa5wR7saNX", "415K", "@zahraa.nature"),
    ("DdKNuPmIdH4", "411K", "@zahraa.nature")
]

for code, views, acc in cands:
    img_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
    if os.path.exists(img_path):
        print(f"Frame already exists: {img_path}")
        continue
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"Capturing {code} ({views} | {acc})...")
    post("/navigate", {"sessionId": session_id, "url": url})
    time.sleep(4.0)

    # Pause video at 2.5s
    post("/evaluate", {"sessionId": session_id, "expression": """
    (() => {
        const v = document.querySelector('video');
        if (v) { v.pause(); v.currentTime = 2.5; }
        return true;
    })()
    """})
    time.sleep(1.0)

    cmd_data = {
        "method": "Page.captureScreenshot",
        "params": {"format": "png"},
        "sessionId": session_id
    }
    ss_res = post("/cmd", cmd_data)
    b64 = ss_res.get("result", {}).get("data")
    if b64:
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"  + Saved: {img_path}")
    else:
        print(f"  - Failed screenshot: {code}")
