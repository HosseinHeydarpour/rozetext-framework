import urllib.request
import json
import time
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

BRIDGE = "http://127.0.0.1:9223"
TARGET_ID = "B6E44804798D56AB8786A0DCD7C982CE"

def post(endpoint, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BRIDGE}{endpoint}", data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode('utf-8'))

# Attach
res = post("/attach", {"targetId": TARGET_ID})
session_id = res.get("sessionId")
print(f"Attached. Session: {session_id}")

accounts_to_scrape = [
    "heliumm.__",
    "sayehmah_",
    "wiiraneh",
    "parvaa_edit",
    "tan___ha28a",
    "itrephe",
    "delneveshteh_shahrzad",
    "ghalbe_daroon",
    "harfamine",
    "boqzdel"
]

harvested = []

for acc in accounts_to_scrape:
    url = f"https://www.instagram.com/{acc}/reels/"
    print(f"\nScraping {acc} ({url})...")
    try:
        post("/navigate", {"sessionId": session_id, "url": url})
        time.sleep(5)

        # Scroll 3 times
        for s in range(3):
            post("/evaluate", {"sessionId": session_id, "expression": "window.scrollBy(0, 1800);"})
            time.sleep(2)

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
        print(f"Found {len(reels)} reels for {acc}")
        
        for r in reels:
            txt = r.get("text", "")
            # parse views
            views = 0
            if "M" in txt:
                try: views = int(float(txt.replace("M", "").strip()) * 1_000_000)
                except: views = 1_000_000
            elif "K" in txt:
                try: views = int(float(txt.replace("K", "").strip()) * 1_000)
                except: views = 0
            
            if views >= 400_000:
                harvested.append({
                    "account": f"@{acc}",
                    "shortcode": r["code"],
                    "url": r["href"],
                    "views": views,
                    "views_str": txt.replace("\n", " ")
                })
                print(f"  + High View: {r['code']} | {views:,} | {txt.replace(chr(10), ' ')}")
    except Exception as e:
        print(f"Error scraping {acc}: {e}")

out_path = "data/fresh_bridge_harvested_reels.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(harvested, f, ensure_ascii=False, indent=2)

print(f"\n==========================================")
print(f"Harvested {len(harvested)} high-view reels to {out_path}")
print(f"==========================================")
