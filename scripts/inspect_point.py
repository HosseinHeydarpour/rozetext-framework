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
    const el = document.elementFromPoint(250, 250);
    if (!el) return "No element at 250,250";
    let cur = el;
    const hierarchy = [];
    while (cur && cur !== document.body) {
        hierarchy.push({
            tag: cur.tagName,
            className: cur.className,
            href: cur.getAttribute('href'),
            role: cur.getAttribute('role'),
            text: (cur.innerText || '').slice(0, 40)
        });
        cur = cur.parentElement;
    }
    return hierarchy;
})()
"""
res2 = post("/evaluate", {"sessionId": s, "expression": js})
print(json.dumps(res2.get("value"), indent=2))
