import asyncio
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from chrome_cdp import ChromeCDP

def parse_views(s):
    if not s:
        return 0
    s = s.upper().replace(',', '').strip()
    if 'M' in s:
        try:
            return int(float(s.replace('M', '')) * 1000000)
        except:
            return 0
    if 'K' in s:
        try:
            return int(float(s.replace('K', '')) * 1000)
        except:
            return 0
    try:
        return int(s)
    except:
        return 0

async def harvest_accounts(accs):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    all_reels = []
    seen_shortcodes = set()

    for acc in accs:
        clean_acc = acc.replace('@', '').strip()
        url = f"https://www.instagram.com/{clean_acc}/reels/"
        print(f"\nChecking {acc} ({url})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)
        
        # Scroll 4 times to load ~40-60 reels
        for _ in range(4):
            await cdp.evaluate(sid, "window.scrollBy(0, 1600);")
            await asyncio.sleep(1.5)
            
        script = """
        (() => {
            let links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
            let data = [];
            for (let a of links) {
                let href = a.href;
                let spans = Array.from(a.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean);
                data.push({href: href, spans: spans});
            }
            return data;
        })()
        """
        res = await cdp.evaluate(sid, script) or []
        print(f"  Found {len(res)} reels in DOM for {acc}")
        
        found_for_acc = 0
        for r in res:
            href = r['href']
            shortcode = href.strip('/').split('/')[-1]
            if shortcode in seen_shortcodes:
                continue
            spans = r['spans']
            max_v = 0
            best_span = ''
            for sp in spans:
                v = parse_views(sp)
                if v > max_v:
                    max_v = v
                    best_span = sp
            if max_v >= 450000:
                seen_shortcodes.add(shortcode)
                all_reels.append({
                    'account': acc,
                    'url': href,
                    'shortcode': shortcode,
                    'views': max_v,
                    'views_str': best_span
                })
                found_for_acc += 1
                print(f"    [+] {shortcode} | {best_span} ({max_v:,} views)")
        print(f"  Qualified >=450K: {found_for_acc} reels")

    await cdp.close()
    return all_reels

if __name__ == "__main__":
    acc_list = [
        '@sayehmah_',
        '@deep_dari9',
        '@_khaazaan_',
        '@text.love400',
        '@delneveshtee_naab',
        '@shadighorbanyy',
        '@ghalbe_daroon',
        '@pouneh_ir',
        '@tavan_sangin',
        '@matne_ziba',
        '@savad_zendegi'
    ]
    reels = asyncio.run(harvest_accounts(acc_list))
    print(f"\n==========================================")
    print(f"Total high-view reels found: {len(reels)}")
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fresh_harvested_batch.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reels, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_path}")
