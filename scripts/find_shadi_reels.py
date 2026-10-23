import urllib.request
import json
import time
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
session_id = res.get("sessionId")

url = "https://www.instagram.com/shadighorbanyy/reels/"
post("/navigate", {"sessionId": session_id, "url": url})
time.sleep(4.0)

# Let's scroll slowly and look at anchors
for s in range(4):
    post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 1200);"})
    time.sleep(1.5)

js = """
(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
    return anchors.map(a => {
        const img = a.querySelector('img');
        const alt = img ? img.getAttribute('alt') : '';
        const href = a.getAttribute('href');
        return { href: href, alt: alt, text: a.innerText };
    });
})()
"""
raw_res = post("/evaluate", {"sessionId": session_id, "expression": js})
items = raw_res.get("value") or []
print(f"Total found: {len(items)}")
for it in items:
    txt = it.get('text', '').replace('\n', ' ')
    alt = it.get('alt', '').replace('\n', ' ')
    print(it.get('href'), '|', txt, '|', alt[:40])
