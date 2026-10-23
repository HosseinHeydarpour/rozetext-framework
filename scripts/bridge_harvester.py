import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = "http://127.0.0.1:9223"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

# 1. Attach to target
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"
attach_res = post("/attach", {"targetId": TARGET_ID})
session_id = attach_res.get("sessionId")
print(f"Attached. Session: {session_id}")

# 2. Navigate to text.love400 reels
print("Navigating to https://www.instagram.com/text.love400/reels/ ...")
post("/navigate", {"sessionId": session_id, "url": "https://www.instagram.com/text.love400/reels/"})
time.sleep(5)

# 3. Scroll to load
for i in range(4):
    post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 1800);"})
    time.sleep(2)

# 4. Extract reels
extract_js = """
(() => {
    const links = Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/reels/"]'));
    const items = [];
    const seen = new Set();
    for (const a of links) {
        const m = a.href.match(/reel[s]?\\/([^\\/]+)/);
        if (!m) continue;
        const code = m[1];
        if (seen.has(code)) continue;
        seen.add(code);
        const text = a.innerText || '';
        items.push({ code, text, href: a.href });
    }
    return items;
})()
"""

res = post("/evaluate", {"sessionId": session_id, "expression": extract_js})
reels = res.get("value", [])
print(f"Extracted {len(reels)} reels from text.love400:")
for r in reels[:15]:
    print(f"  {r['code']} | Views/Text: {r['text'].replace(chr(10), ' ')}")
