import asyncio
import json
import os
import random
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

BENCHMARK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_accounts.json")

def load_all_profiles():
    if os.path.exists(BENCHMARK_PATH):
        with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        return [a.get("handle", "").replace("@", "").strip() for a in d.get("accounts", [])]
    return ["text.love400", "leyli_geraphy", "docharetooo", "atiya_text", "matne_ziba", "savad_zendegi"]

async def harvest_all(max_accounts=15):
    profiles = load_all_profiles()
    print(f"[*] Loaded {len(profiles)} benchmark profiles from {BENCHMARK_PATH}")
    
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '')]
    if not ig_targets:
        print("[!] Error: No Instagram tab found in Chrome.")
        await cdp.close()
        return
        
    sid = await cdp.attach_page(ig_targets[0]['targetId'])
    print(f"[*] Attached to Instagram tab: {ig_targets[0].get('title', '')}")
    
    processed = 0
    for username in profiles:
        if processed >= max_accounts:
            break
            
        out_file = f"data/harvest_{username}.json"
        if os.path.exists(out_file) and os.path.getsize(out_file) > 100:
            continue
            
        url = f"https://www.instagram.com/{username}/reels/"
        print(f"\n({processed+1}/{max_accounts}) Navigating to {url}...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(random.uniform(4.0, 6.0))
        
        # Polite gradual scroll
        for i in range(4):
            scroll_by = random.randint(500, 900)
            await cdp.evaluate(sid, f"window.scrollBy(0, {scroll_by});")
            await asyncio.sleep(random.uniform(1.8, 3.0))
            
        js = """
        (() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
            const seen = new Set();
            const results = [];
            for (const a of anchors) {
                const href = a.getAttribute('href');
                if (!href || seen.has(href)) continue;
                seen.add(href);
                const text = a.innerText.trim();
                const spans = Array.from(a.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean);
                results.push({
                    href: href,
                    text: text,
                    spans: spans
                });
            }
            return results;
        })()
        """
        reels = await cdp.evaluate(sid, js)
        print(f"[+] Harvested {len(reels)} unique reels from @{username}")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(reels, f, ensure_ascii=False, indent=2)
            
        processed += 1
        await asyncio.sleep(random.uniform(2.5, 4.0))
            
    await cdp.close()
    print(f"\n[DONE] Finished harvesting batch of {processed} profiles.")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(harvest_all(max_accounts=count))
