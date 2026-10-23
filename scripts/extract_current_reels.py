import urllib.request
import json

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
s = res.get("sessionId")

js = """
(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
    return anchors.map(a => {
        const href = a.getAttribute('href');
        const m = href.match(/\\/reel\\/([A-Za-z0-9_-]+)/);
        return {
            code: m ? m[1] : '',
            href: 'https://www.instagram.com/reel/' + (m ? m[1] : '') + '/',
            views: a.innerText.trim().replace(/\\n/g, ' ')
        };
    });
})()
"""
res2 = post("/evaluate", {"sessionId": s, "expression": js})
items = res2.get("value", [])
print(f"Total reel links on current page: {len(items)}")
for it in items:
    print(f"{it['code']:<16} | {it['views']:<10} | {it['href']}")
