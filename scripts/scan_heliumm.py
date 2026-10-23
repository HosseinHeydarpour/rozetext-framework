import urllib.request
import json
import time

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
s = res.get("sessionId")

def parse_views(v_str):
    v = v_str.strip().upper().replace(',', '')
    if 'M' in v:
        return float(v.replace('M', '')) * 1_000_000
    if 'K' in v:
        return float(v.replace('K', '')) * 1_000
    try:
        return float(v)
    except:
        return 0

url = "https://www.instagram.com/heliumm.__/reels/"
print(f"Navigating to {url}...")
post("/navigate", {"sessionId": s, "url": url})
time.sleep(5)

def get_visible_reels():
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
    res = post("/evaluate", {"sessionId": s, "expression": js})
    return res.get("value", [])

all_reels = {}
for scroll in range(12):
    for it in get_visible_reels():
        if it['code'] and it['code'] not in all_reels:
            it['views_num'] = parse_views(it['views_str'])
            all_reels[it['code']] = it
    print(f"Scroll {scroll+1}: Total collected = {len(all_reels)}")
    post("/evaluate", {"sessionId": s, "expression": "window.scrollBy(0, 2000);"})
    time.sleep(2.0)

high_reels = [r for r in all_reels.values() if r['views_num'] >= 350_000]
high_reels.sort(key=lambda x: x['views_num'], reverse=True)
print(f"\nTotal reels with >= 350K from @heliumm.__: {len(high_reels)}")
for r in high_reels:
    print(f"{r['code']:<16} | {r['views_str']:<10} | {r['href']}")

with open("downloads/heliumm_high.json", "w", encoding="utf-8") as f:
    json.dump(high_reels, f, ensure_ascii=False, indent=2)
