import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

BIG_PROFILES = [
    "matne_ziba",
    "halekhoub",
    "delltherapy",
    "vahidrezakhoshbayan",
    "imazhart",
    "sepehr_kh",
    "hichpouch",
    "book.icy"
]

SYSTEM_PATHS = {
    'explore', 'reels', 'direct', 'stories', 'accounts', 'legal', 'popular',
    'about', 'privacy', 'terms', 'language', 'help', 'press', 'api', 'jobs',
    'locations', 'meta_verified', 'hosseinheydarpour'
}

async def extract_suggestions():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("[!] No IG tab.")
        await cdp.close()
        return
        
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    discovered = set()
    
    for prof in BIG_PROFILES:
        print(f"[*] Navigating to @{prof}...")
        await cdp.navigate(sid, f"https://www.instagram.com/{prof}/")
        await asyncio.sleep(4.5)
        
        # Look for the suggested accounts button and click it to reveal carousel
        click_suggest_script = """
        (() => {
            // Find button next to Follow/Message that shows suggested accounts (often has svg with person+plus or arrow)
            const btns = Array.from(document.querySelectorAll('button, div[role="button"]'));
            for (const b of btns) {
                if (b.querySelector('svg[aria-label*="Similar"], svg[aria-label*="مشابه"], svg[aria-label*="پیشنهاد"]')) {
                    b.click();
                    return true;
                }
            }
            return false;
        })()
        """
        clicked = await cdp.evaluate(sid, click_suggest_script)
        if clicked:
            print("  [+] Clicked suggested accounts button! Waiting 3s...")
            await asyncio.sleep(3.0)
            
        extract_script = """
        (() => {
            const links = Array.from(document.querySelectorAll('a[href^="/"]'));
            const accounts = [];
            for (const a of links) {
                const h = a.getAttribute('href') || '';
                const m = h.match(/^\\/([a-zA-Z0-9_\\.]+)\\/$/);
                if (m) {
                    accounts.push(m[1].toLowerCase());
                }
            }
            return accounts;
        })()
        """
        found = await cdp.evaluate(sid, extract_script)
        for cand in (found or []):
            if cand not in SYSTEM_PATHS and cand not in BIG_PROFILES and len(cand) > 2:
                discovered.add(cand)
                
        print(f"  Total unique candidates so far: {len(discovered)}")
        await asyncio.sleep(2.0)
        
    with open("data/graph_discovered_candidates.json", "w", encoding="utf-8") as f:
        json.dump(list(discovered), f, ensure_ascii=False, indent=2)
        
    print(f"\n[DONE] Discovered {len(discovered)} potential candidate handles from Instagram Graph!")
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(extract_suggestions())
