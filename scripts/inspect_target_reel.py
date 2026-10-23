import urllib.request
import json
import time
import base64
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"
FRAMES_DIR = "downloads/frames"
os.makedirs(FRAMES_DIR, exist_ok=True)

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
session_id = res.get("sessionId")
print(f"Attached. Session: {session_id}")

shortcode = "DbQ5ACmslaO"
url = f"https://www.instagram.com/reel/{shortcode}/"
print(f"Navigating to {url}...")
post("/navigate", {"sessionId": session_id, "url": url})
time.sleep(4.0)

# Check caption and pause video
js_info = """
(() => {
    const v = document.querySelector('video');
    if (v) {
        v.pause();
        v.currentTime = 3.0;
    }
    const captionEl = document.querySelector('h1, span._ap3a._aaco._aacu._aacx._aad7._aade');
    return {
        title: document.title,
        caption: captionEl ? captionEl.innerText : '',
        bodyText: document.body.innerText.substring(0, 500)
    };
})()
"""
info = post("/evaluate", {"sessionId": session_id, "expression": js_info})
print("Page Info:", info)

time.sleep(1.5)

# Screenshot
out_path = os.path.join(FRAMES_DIR, f"{shortcode}_frame.png")
shot = post("/capture_screenshot", {"sessionId": session_id, "output_path": out_path})
print("Screenshot result:", shot)
