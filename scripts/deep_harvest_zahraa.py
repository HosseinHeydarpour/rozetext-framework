import urllib.request
import json
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = 'http://127.0.0.1:9223'
TARGET_ID = 'B6E44804798D56AB8786A0DCD7C982CE'

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post('/attach', {'targetId': TARGET_ID})
session_id = res.get('sessionId')
print(f"Attached session: {session_id}")

post('/navigate', {'sessionId': session_id, 'url': 'https://www.instagram.com/zahraa.nature/reels/'})
time.sleep(3.5)

# Scroll 12 times to reach deeper reels
for s in range(12):
    post('/evaluate', {'sessionId': session_id, 'expression': 'window.scrollBy(0, 1500);'})
    time.sleep(1.2)

js = """
(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
    return anchors.map(a => {
        const href = a.getAttribute('href');
        return { href: href, text: a.innerText };
    });
})()
"""
raw_res = post('/evaluate', {'sessionId': session_id, 'expression': js})
items = raw_res.get('value') or []
print(f"Total found: {len(items)}")

seen = set()
unique = []
for it in items:
    h = it.get('href')
    if h and h not in seen:
        seen.add(h)
        unique.append(it)

with open('data/harvest_zahraa_deep.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"Saved {len(unique)} unique reels to data/harvest_zahraa_deep.json")
