import urllib.request
import json
import time
import sys
import base64
import os

sys.stdout.reconfigure(encoding='utf-8')

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
print(f"Attached session: {session_id}")

reels = [
    ("DG8jFKGIWjY", "9.7M", "@texthayedeli.ir"),
    ("DHMRcwUIAiZ", "2.8M", "@texthayedeli.ir"),
    ("DHwBbAooihl", "2.4M", "@texthayedeli.ir"),
    ("DIKL9gZqM6_", "3.6M", "@texthayedeli.ir"),
    ("DHB_vZVIUrZ", "2.8M", "@texthayedeli.ir"),
    ("DHlVVNkoJOC", "2.7M", "@texthayedeli.ir"),
    ("DIb_vRgqk58", "2.2M", "@texthayedeli.ir"),
    ("DHy7292o-GE", "2.0M", "@texthayedeli.ir"),
    ("DPhK0fYCKcn", "1.8M", "@_be_yar"),
    ("DZ5bbDAoRSq", "2.2M", "@_be_yar"),
    ("DZAuJ6aIfsq", "1.8M", "@_be_yar"),
    ("DCWQZ16gZMI", "9.9M", "@boqzdel")
]

for code, views, acc in reels:
    img_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
    if os.path.exists(img_path):
        print(f"Frame exists: {img_path}")
        continue
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"Capturing {code} ({views} | {acc})...")
    post("/navigate", {"sessionId": session_id, "url": url})
    time.sleep(4.0)

    # Pause video at 2.0s
    post("/evaluate", {"sessionId": session_id, "expression": """
    (() => {
        const v = document.querySelector('video');
        if (v) { v.pause(); v.currentTime = 2.0; }
        return true;
    })()
    """})
    time.sleep(0.8)

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
        print(f"  + Saved {img_path}")
    else:
        print(f"  - Failed {code}")

print("\nDone capturing batch!")
