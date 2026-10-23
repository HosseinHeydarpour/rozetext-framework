import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.chrome_cdp import ChromeCDP

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

async def harvest_expanded():
    with open("data/scripts-db.json", "r", encoding="utf-8") as f:
        db = json.load(f)
    db_shortcodes = set()
    for s in db.get("scripts", []):
        u = s.get("source_url", "")
        if u:
            db_shortcodes.add(u.strip("/").split("/")[-1])

    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    accounts = [
        "@sayehmah_",
        "@text.love400",
        "@_khaazaan_",
        "@vahidrezakhoshbayan",
        "@alikeshavarz.original",
        "@haarmuni",
        "@delneveshtee_naab",
        "@matne_ziba",
        "@atiya_text",
        "@docharetooo",
        "@leyli_geraphy",
        "@sepehr_kh",
        "@horaetemad",
        "@radio.khat",
        "@pouneh_ir"
    ]
    
    all_harvested = []
    seen = set()

    for acc in accounts:
        handle = acc.replace("@", "").strip()
        url = f"https://www.instagram.com/{handle}/reels/"
        print(f"\n[+] Navigating to {acc} ({url})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)
        
        # Scroll down 6 times with delay to let infinite scroll load
        for scroll_i in range(6):
            await cdp.evaluate(sid, "window.scrollBy(0, 1800);")
            await asyncio.sleep(1.2)
            
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
        print(f"    DOM links found: {len(res)}")
        
        qualified_cnt = 0
        for r in res:
            href = r['href']
            shortcode = href.strip("/").split("/")[-1]
            if shortcode in seen or shortcode in db_shortcodes:
                continue
            
            # Extract max view count
            max_v = 0
            best_span = ""
            for sp in r['spans']:
                v = parse_views(sp)
                if v > max_v:
                    max_v = v
                    best_span = sp
                    
            if max_v >= 450000:
                seen.add(shortcode)
                all_harvested.append({
                    "account": acc,
                    "url": href,
                    "shortcode": shortcode,
                    "views": max_v,
                    "views_str": best_span
                })
                qualified_cnt += 1
                print(f"      -> {shortcode} | {best_span} ({max_v:,} views)")
                
        print(f"    Qualified from {acc}: {qualified_cnt}")

    await cdp.close()
    
    out_file = "data/expanded_hunted_pool.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_harvested, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Successfully harvested {len(all_harvested)} reels with >=450K views!")
    print(f"Saved to {out_file}")

if __name__ == "__main__":
    asyncio.run(harvest_expanded())
