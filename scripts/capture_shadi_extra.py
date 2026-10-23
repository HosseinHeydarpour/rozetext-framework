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

url = "https://www.instagram.com/shadighorbanyy/reels/"
post("/navigate", {"sessionId": session_id, "url": url})
time.sleep(4.0)

# Scroll to load older reels
for scroll in range(5):
    post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 2000);"})
    time.sleep(2.0)

js = """
(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
    return anchors.map(a => {
        const href = a.getAttribute('href');
        const m = href.match(/\\/reel\\/([A-Za-z0-9_-]+)/);
        return {
            code: m ? m[1] : '',
            href: 'https://www.instagram.com/reel/' + (m ? m[1] : '') + '/',
            views_str: a.innerText.trim().replace(/\\n/g, ' ')
        };
    });
})()
"""
raw_res = post("/evaluate", {"sessionId": session_id, "expression": js})
reels = raw_res.get("value") or []
print(f"Found {len(reels)} reels on @shadighorbanyy")

already_done = {'DdHKlyLKHs4', 'DdeYIgZqlG9', 'DdhIZDEK8_S', 'DdotWXnCiBy', 'DdzFv9hCAZO', 'DdwZAGeBgNq'}
candidates = [r for r in reels if r['code'] and r['code'] not in already_done]
print(f"Candidates to inspect: {len(candidates)}")

for idx, c in enumerate(candidates[:8], 1):
    code = c['code']
    frame_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
    print(f"[{idx}] Capturing {code} ({c['views_str']})...")
    post("/navigate", {"sessionId": session_id, "url": c['href']})
    time.sleep(4.0)

    # Pause at 3.0s (some reels start black)
    post("/evaluate", {"sessionId": session_id, "expression": """
    (() => {
        const v = document.querySelector('video');
        if (v) { v.pause(); v.currentTime = 3.5; }
        return true;
    })()
    """})
    time.sleep(1.0)

    ss_res = post("/cmd", {
        "method": "Page.captureScreenshot",
        "params": {"format": "png"},
        "sessionId": session_id
    })
    b64 = ss_res.get("result", {}).get("data")
    if b64:
        with open(frame_path, "wb") as f:
            f.write(base64.b64decode(b64))
        print(f"  + Saved: {frame_path}")

print("Done capturing shadi extra reels.")
