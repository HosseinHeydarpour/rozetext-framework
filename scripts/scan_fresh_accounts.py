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

def parse_views(v_str):
    if not v_str:
        return 0
    s = v_str.replace(',', '').strip()
    if 'M' in s:
        return float(s.replace('M', '')) * 1000000
    if 'K' in s:
        return float(s.replace('K', '')) * 1000
    try:
        return float(s)
    except:
        return 0

accounts_to_scan = [
    "delneveshtee_naab",
    "tavan_sangin",
    "boqzdel"
]

all_high_reels = []

for acc in accounts_to_scan:
    url = f"https://www.instagram.com/{acc}/reels/"
    print(f"\n--- Navigating to {url} ---")
    post("/navigate", {"sessionId": session_id, "url": url})
    time.sleep(5.0)

    # Scroll down 4 times to load ~30-40 reels
    for scroll in range(4):
        post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 1500);"})
        time.sleep(2.0)

    extract_js = """
    (() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
        const seen = new Set();
        const results = [];
        for (const a of anchors) {
            const href = a.getAttribute('href');
            if (!href || seen.has(href)) continue;
            seen.add(href);
            const text = a.innerText.trim();
            results.push({ href: href, text: text });
        }
        return results;
    })()
    """
    raw_res = post("/evaluate", {"sessionId": session_id, "expression": extract_js})
    reels_found = raw_res.get("value") or []
    print(f"Found {len(reels_found)} total reels on @{acc}")

    for r in reels_found:
        href = r.get("href", "")
        txt = r.get("text", "")
        # parse code
        parts = [p for p in href.split('/') if p]
        code = parts[-1] if parts else ""
        # The text inside a[href*="/reel/"] usually contains view count e.g. "1.2M", "540K"
        v_num = parse_views(txt)
        if v_num >= 350000 or 'M' in txt or ('K' in txt and v_num >= 350000):
            item = {
                "account": f"@{acc}",
                "code": code,
                "url": f"https://www.instagram.com/reel/{code}/",
                "views_str": txt,
                "views_num": v_num
            }
            all_high_reels.append(item)
            print(f"  + High Reel: {code} | {txt} | @{acc}")

print(f"\nTotal high reels collected: {len(all_high_reels)}")
with open('downloads/fresh_scanned_high.json', 'w', encoding='utf-8') as f:
    json.dump(all_high_reels, f, ensure_ascii=False, indent=2)
