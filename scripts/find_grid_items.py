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
    const anchors = Array.from(document.querySelectorAll('a'));
    return anchors.map(a => {
        const rect = a.getBoundingClientRect();
        return {
            href: a.getAttribute('href') || a.href,
            text: a.innerText.trim().replace(/\\n/g, ' '),
            top: Math.round(rect.top),
            left: Math.round(rect.left),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
        };
    }).filter(x => x.width > 50 && x.height > 50);
})()
"""
res2 = post("/evaluate", {"sessionId": s, "expression": js})
items = res2.get("result", {}).get("result", {}).get("value", [])
print(f"Total grid items: {len(items)}")
for it in items:
    print(f"y={it['top']:<4} x={it['left']:<4} | {it['text']:<12} | {it['href']}")
