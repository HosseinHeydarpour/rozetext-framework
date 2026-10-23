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

def parse_views(v_str):
    if not v_str:
        return 0
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    for i, d in enumerate(persian_digits):
        v_str = v_str.replace(d, str(i))
    v = v_str.strip().upper().replace(',', '')
    if 'M' in v:
        try:
            return float(v.split('M')[0].strip()) * 1_000_000
        except:
            pass
    if 'K' in v:
        try:
            return float(v.split('K')[0].strip()) * 1_000
        except:
            pass
    try:
        return float(v)
    except:
        return 0

accounts = ["chicheknaz", "delkook", "hichpouchstory"]
all_high = []

for acc in accounts:
    url = f"https://www.instagram.com/{acc}/reels/"
    print(f"\nNavigating to {url}...")
    post("/navigate", {"sessionId": session_id, "url": url})
    time.sleep(5.0)

    acc_reels = {}
    for scroll in range(6):
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
        reels_list = raw_res.get("value") or []
        for r in reels_list:
            code = r.get("code")
            if code and code not in acc_reels:
                r['views_num'] = parse_views(r.get('views_str', ''))
                r['account'] = f"@{acc}"
                acc_reels[code] = r
        post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 2000);"})
        time.sleep(2.0)

    high = [r for r in acc_reels.values() if r['views_num'] >= 300_000]
    high.sort(key=lambda x: x['views_num'], reverse=True)
    print(f"Total >= 300K for @{acc}: {len(high)}")
    for hr in high[:6]:
        print(f"  {hr['code']} | {hr['views_str']} | {hr['views_num']:,.0f}")
        all_high.append(hr)

print(f"\nCapturing {len(all_high)} candidate frames...")
for idx, r in enumerate(all_high, 1):
    code = r['code']
    frame_path = os.path.join(FRAMES_DIR, f"{code}_frame.png")
    if os.path.exists(frame_path) and os.path.getsize(frame_path) > 10000:
        print(f"[{idx}] Exists: {code}")
        continue
    print(f"[{idx}] Capturing {code} ({r['views_str']} | {r['account']})...")
    post("/navigate", {"sessionId": session_id, "url": r['href']})
    time.sleep(4.0)

    post("/evaluate", {"sessionId": session_id, "expression": """
    (() => {
        const v = document.querySelector('video');
        if (v) { v.pause(); v.currentTime = 2.5; }
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

print("Done scanning chicheknaz, delkook, hichpouchstory.")
