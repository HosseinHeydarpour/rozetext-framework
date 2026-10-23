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

candidates = [
    ("C_tJLJQx_7T", "11.4M", "@vahidrezakhoshbayan"),
    ("DChXfbBRDFR", "7.6M", "@vahidrezakhoshbayan"),
    ("DbQ5ACmslaO", "1.3M", "@vahidrezakhoshbayan"),
    ("DR7fbNlCBle", "996K", "@vahidrezakhoshbayan"),
    ("DaN7SayomTk", "972K", "@vahidrezakhoshbayan"),
    ("DRpeLe-iMDr", "941K", "@vahidrezakhoshbayan"),
    ("DRaEpxbDdel", "752K", "@vahidrezakhoshbayan"),
    ("DS0LBApiHx1", "500K", "@vahidrezakhoshbayan"),
    ("DZiJyf3ImZl", "454K", "@vahidrezakhoshbayan"),
    ("DaGOw9oNrHy", "425K", "@vahidrezakhoshbayan"),
    ("Dd9GQ7HsdZM", "1.5M", "@text.love400"),
    ("DeHZ8jssKkR", "957K", "@text.love400"),
    ("DeCTEN2s-b2", "382K", "@text.love400"),
    ("DeKub9fOhXP", "379K", "@text.love400"),
    ("DeOgNk1IILE", "373K", "@text.love400")
]

for code, views, acc in candidates:
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
