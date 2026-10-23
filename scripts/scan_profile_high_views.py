import urllib.request
import json
import time
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
s = res.get("sessionId")
print(f"Attached. Session: {s}")

def parse_views(v_str):
    v_str = v_str.strip().upper()
    if not v_str:
        return 0
    try:
        if 'M' in v_str:
            return float(v_str.replace('M', '').replace(',', '')) * 1_000_000
        elif 'K' in v_str:
            return float(v_str.replace('K', '').replace(',', '')) * 1_000
        else:
            return float(v_str.replace(',', ''))
    except:
        return 0

def scan_account(username, max_scrolls=8):
    url = f"https://www.instagram.com/{username}/reels/"
    print(f"\n==========================================")
    print(f"Scanning @{username} at {url}...")
    post("/navigate", {"sessionId": s, "url": url})
    time.sleep(5)
    
    seen = {}
    for scroll in range(max_scrolls):
        js = """
        (() => {
            const main = document.querySelector('main');
            if (!main) return [];
            return Array.from(main.querySelectorAll('a')).map(a => ({
                href: a.href,
                text: a.innerText.trim()
            })).filter(x => x.href.includes('/reel/'));
        })()
        """
        res2 = post("/evaluate", {"sessionId": s, "expression": js})
        items = res2.get("result", {}).get("result", {}).get("value", [])
        for it in items:
            m = re.search(r'/reel/([A-Za-z0-9_-]+)', it['href'])
            if m:
                code = m.group(1)
                text = it['text'].replace('\n', ' ')
                views = parse_views(text)
                if code not in seen:
                    seen[code] = {
                        "code": code,
                        "views_str": text,
                        "views_num": views,
                        "url": f"https://www.instagram.com/reel/{code}/",
                        "author": f"@{username}"
                    }
        print(f"  Scroll {scroll+1}/{max_scrolls}: Total unique reels found so far = {len(seen)}")
        post("/evaluate", {"sessionId": s, "expression": "window.scrollBy(0, 1500);"})
        time.sleep(2.5)

    all_reels = list(seen.values())
    all_reels.sort(key=lambda x: x['views_num'], reverse=True)
    high_views = [r for r in all_reels if r['views_num'] >= 450_000]
    print(f"\nFound {len(high_views)} reels with >= 450K views for @{username}:")
    for r in high_views:
        print(f"  {r['code']} | {r['views_str']:<8} | {r['url']}")
    return high_views

if __name__ == "__main__":
    acc = sys.argv[1] if len(sys.argv) > 1 else "zahraa.nature"
    reels = scan_account(acc, max_scrolls=10)
    with open(f"downloads/{acc}_high_reels.json", "w", encoding="utf-8") as f:
        json.dump(reels, f, ensure_ascii=False, indent=2)
