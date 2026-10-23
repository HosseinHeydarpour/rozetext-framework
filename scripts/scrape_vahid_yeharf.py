import urllib.request
import json
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=50) as resp:
        return json.loads(resp.read().decode('utf-8'))

res = post("/attach", {"targetId": TARGET_ID})
session_id = res.get("sessionId")

target_accounts = [
    "vahidrezakhoshbayan",
    "___yeharf"
]

all_extracted = []

for acc in target_accounts:
    print(f"\nScraping @{acc}...")
    post("/navigate", {"sessionId": session_id, "url": f"https://www.instagram.com/{acc}/reels/"})
    time.sleep(5.0)

    for s in range(5):
        post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 1800);"})
        time.sleep(2.0)

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
    print(f"Loaded {len(reels)} reels for @{acc}")

    for r in reels:
        txt = r.get("text", "")
        views = 0
        if "M" in txt:
            try: views = int(float(txt.replace("M", "").strip()) * 1_000_000)
            except: views = 1_000_000
        elif "K" in txt:
            try: views = int(float(txt.replace("K", "").strip()) * 1_000)
            except: views = 0
        elif txt.replace(",", "").isdigit():
            views = int(txt.replace(",", ""))

        if views >= 400_000:
            all_extracted.append({
                "account": f"@{acc}",
                "code": r["code"],
                "url": r["href"],
                "views": views,
                "views_str": txt.replace("\n", " ")
            })
            print(f"  + High View: {r['code']} | {views:,} ({txt.replace(chr(10), ' ')})")

out_file = "data/scraped_vahid_yeharf.json"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(all_extracted, f, ensure_ascii=False, indent=2)
