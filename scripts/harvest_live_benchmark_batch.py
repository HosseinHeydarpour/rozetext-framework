import asyncio
import json
import os
import sys
import random
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine

async def harvest_accounts(accounts, deep_scroll=8, min_views=500000):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("[!] No IG tab found")
        return []
        
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    engine = AntiDuplicationEngine.get_instance()
    
    db_path = 'data/scripts-db.json'
    db_urls = set()
    if os.path.exists(db_path):
        db = json.load(open(db_path, encoding='utf-8'))
        db_urls = {s.get('source_url') for s in db.get('scripts', []) if s.get('source_url')}

    all_qualifying = []

    for acc_idx, acc in enumerate(accounts, 1):
        print(f"\n[{acc_idx}/{len(accounts)}] Navigating to @{acc}/reels/...")
        await cdp.navigate(sid, f"https://www.instagram.com/{acc}/reels/")
        await asyncio.sleep(4.0)

        # Deep scroll
        for s in range(deep_scroll):
            scroll_amt = random.randint(600, 950)
            await cdp.evaluate(sid, f"window.scrollBy(0, {scroll_amt})")
            await asyncio.sleep(1.8)

        # Extract reel links and badges
        grid_js = """
        (() => {
            let links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
            let data = [];
            for (let a of links) {
                let href = a.href;
                let spans = Array.from(a.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean);
                data.push({url: href, badges: spans});
            }
            return data;
        })()
        """
        reels = await cdp.evaluate(sid, grid_js) or []
        print(f"   -> Found {len(reels)} reel elements on @{acc}")

        for r in reels:
            url = r.get("url", "")
            if not url or url in db_urls:
                continue
            badges = r.get("badges", [])
            views_num = 0
            views_str = "0"
            for b in badges:
                b_clean = b.replace(',', '').replace('،', '').strip()
                if 'M' in b_clean:
                    try:
                        views_num = int(float(b_clean.replace('M', '')) * 1000000)
                        views_str = b
                    except: pass
                elif 'K' in b_clean:
                    try:
                        views_num = int(float(b_clean.replace('K', '')) * 1000)
                        views_str = b
                    except: pass

            if views_num >= min_views or 'M' in views_str:
                shortcode = url.strip('/').split('/')[-1]
                entry = {
                    "account": f"@{acc}",
                    "url": url,
                    "shortcode": shortcode,
                    "views": views_num,
                    "views_str": views_str
                }
                all_qualifying.append(entry)
                print(f"      [+] Qualifying viral reel: {url} ({views_str} views)")

    await cdp.close()
    out_path = "data/fresh_live_hunted_pool.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_qualifying, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Harvested {len(all_qualifying)} viral reels >= 500K views! Saved to {out_path}")
    return all_qualifying

if __name__ == "__main__":
    target_accounts = [
        "black__text.99",
        "zahraa.nature",
        "_be_yar",
        "samatextt",
        "texthayedeli.ir",
        "sadatamorist",
        "boqzdel",
        "textnime_shab",
        "wiiraneh"
    ]
    asyncio.run(harvest_accounts(target_accounts, deep_scroll=8, min_views=500000))
