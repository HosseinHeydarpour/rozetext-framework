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
print(f"Attached. Session: {session_id}")

reels_to_capture = [
    # vahidrezakhoshbayan
    ("DZDRxCkNgjw", "1.5M", "@vahidrezakhoshbayan"),
    ("DZQJRhRNpQG", "1.3M", "@vahidrezakhoshbayan"),
    ("DZ0MBsJtBT4", "1.9M", "@vahidrezakhoshbayan"),
    ("DbbPmLFNZbj", "1.9M", "@vahidrezakhoshbayan"),
    ("DcjQOwtN86T", "599K", "@vahidrezakhoshbayan"),
    ("Dc1S6FRoBRz", "520K", "@vahidrezakhoshbayan"),
    # heliumm.__
    ("Db5xnQRtceg", "1.2M", "@heliumm.__"),
    ("DcgYgz3Nfh2", "885K", "@heliumm.__"),
    # text.love400
    ("Dcbkrg2shXf", "617K", "@text.love400"),
    ("DcYrztKMhtn", "546K", "@text.love400"),
    # zahraa.nature
    ("Dbv_TqKMl-P", "501K", "@zahraa.nature"),
    ("Dc4FWg8sWFh", "499K", "@zahraa.nature"),
    ("DcHKsdUMpGH", "477K", "@zahraa.nature")
]

for code, views, acc in reels_to_capture:
    img_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
    if os.path.exists(img_path):
        print(f"Frame already exists: {img_path}")
        continue
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"Capturing {code} ({views} | {acc})...")
    post("/navigate", {"sessionId": session_id, "url": url})
    time.sleep(4.5)

    # Pause video
    post("/evaluate", {"sessionId": session_id, "expression": """
    (() => {
        const v = document.querySelector('video');
        if (v) { v.pause(); v.currentTime = 2.0; }
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
