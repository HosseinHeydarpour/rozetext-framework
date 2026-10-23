import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = 'http://127.0.0.1:9223'
TARGET_ID = 'B6E44804798D56AB8786A0DCD7C982CE'

def post(ep, d):
    req = urllib.request.Request(f"{BRIDGE}{ep}", data=json.dumps(d).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode('utf-8'))

res = post('/attach', {'targetId': TARGET_ID})
sid = res['sessionId']

js = """
(() => {
    const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
    return links.map(a => {
        const m = a.href.match(/reel\\/([^\\/]+)/);
        return { code: m ? m[1] : '', text: a.innerText || '' };
    });
})()
"""
items = post('/evaluate', {'sessionId': sid, 'expression': js})['value']
print(f"Total: {len(items)}")
for it in items:
    print(f"{it['code']} --> {it['text'].replace(chr(10), ' ')}")
