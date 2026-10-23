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
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
session_id = res.get("sessionId")
print(f"Attached. Session: {session_id}")

test_reels = [
    ("Deb9FjuIs5e", "@itrephe", "954K"),
    ("DeXpqf0R9at", "@itrephe", "834K"),
    ("DeW4Acmojlr", "@itrephe", "691K"),
    ("Deb3gAtIgV2", "@itrephe", "520K"),
    ("DcMPSAeRgPm", "@delneveshteh_shahrzad", "1.1M"),
    ("DcG_OzzqICV", "@delneveshteh_shahrzad", "982K"),
    ("DMxzPOKir3d", "@harfamine", "1.2M"),
    ("DNOcLxKychh", "@boqzdel", "781K")
]

for code, acc, views in test_reels:
    url = f"https://www.instagram.com/reel/{code}/"
    print(f"\nNavigating to {url} ({views} | {acc})...")
    post("/navigate", {"sessionId": session_id, "url": url})
    time.sleep(4.5)

    # Pause video and capture frame
    prep_js = """
    (() => {
        const v = document.querySelector('video');
        if (v) {
            v.pause();
            v.currentTime = 2.0;
        }
        return { ok: true };
    })()
    """
    post("/evaluate", {"sessionId": session_id, "expression": prep_js})
    time.sleep(1.0)

    # Capture screenshot
    cmd_data = {
        "method": "Page.captureScreenshot",
        "params": {"format": "png"},
        "sessionId": session_id
    }
    ss_res = post("/cmd", cmd_data)
    b64 = ss_res.get("result", {}).get("data")
    if b64:
        img_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"Saved frame: {img_path}")
    else:
        print("Failed to capture screenshot")
