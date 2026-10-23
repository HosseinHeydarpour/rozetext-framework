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
print(f"Attached session: {session_id}")

account = sys.argv[1] if len(sys.argv) > 1 else "horaetemad"
url = f"https://www.instagram.com/{account}/reels/"
print(f"Navigating to {url}...")
post("/navigate", {"sessionId": session_id, "url": url})
time.sleep(3.5)

# Scroll 5 times to load ~30-40 reels
for s in range(5):
    post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 1000);"})
    time.sleep(1.2)

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
print(f"Total reels found for @{account}: {len(items)}")

out_file = f"data/harvest_{account}.json"
seen = set()
unique_items = []
for it in items:
    h = it.get('href')
    if h and h not in seen:
        seen.add(h)
        unique_items.append(it)

with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(unique_items, f, ensure_ascii=False, indent=2)

print(f"Saved {len(unique_items)} unique reels to {out_file}")
for i, it in enumerate(unique_items[:15]):
    t = it.get('text', '').replace('\n', ' ')
    print(f"[{i}] {it.get('href')} | {t}")
