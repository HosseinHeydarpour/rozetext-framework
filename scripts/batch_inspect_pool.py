import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.chrome_cdp import ChromeCDP

async def inspect_pool():
    with open("data/scripts-db.json", "r", encoding="utf-8") as f:
        db = json.load(f)
    db_codes = set()
    for s in db.get("scripts", []):
        u = s.get("source_url", "")
        if u:
            db_codes.add(u.strip("/").split("/")[-1])

    pool_files = [
        "data/expanded_hunted_pool.json",
        "data/fresh_harvested_batch.json",
        "data/fresh_live_hunted_pool.json"
    ]
    
    candidates = []
    seen = set()
    
    for pf in pool_files:
        if os.path.exists(pf):
            with open(pf, "r", encoding="utf-8") as f:
                items = json.load(f)
            for it in items:
                code = it.get("shortcode")
                if code and code not in seen and code not in db_codes:
                    seen.add(code)
                    candidates.append(it)
                    
    print(f"Total unique uninspected candidates in pools: {len(candidates)}")
    
    # Sort candidates by view count descending
    candidates = sorted(candidates, key=lambda x: x.get("views", 0), reverse=True)
    
    # Priority accounts: haarmuni, vahidrezakhoshbayan, text.love400, alikeshavarz.original, sepehr_kh, horaetemad, radio.khat, zahraa.nature
    selected = [c for c in candidates if c.get("account") not in ["@halekhoub"]]
    
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
    os.makedirs(frame_dir, exist_ok=True)
    
    inspected_results = []
    # Inspect top 15 candidates
    to_inspect = selected[:15]
    print(f"Inspecting top {len(to_inspect)} highest-view candidates...")
    
    for idx, c in enumerate(to_inspect, 1):
        url = c["url"]
        code = c["shortcode"]
        acc = c["account"]
        views = c["views_str"]
        print(f"\n[{idx}/{len(to_inspect)}] {code} ({acc} | {views})...")
        
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)
        
        pause_js = """
        (() => {
            let v = document.querySelector('video');
            if (v) { v.currentTime = 2.0; v.pause(); return true; }
            return false;
        })()
        """
        await cdp.evaluate(sid, pause_js)
        await asyncio.sleep(1.0)
        
        frame_path = os.path.join(frame_dir, f"{code}_frame.png")
        await cdp.capture_screenshot(sid, frame_path)
        print(f"  Frame: {frame_path}")
        
        info_js = """
        (() => {
            let h1 = document.querySelector('h1');
            let caption = h1 ? h1.innerText.trim() : '';
            return { caption: caption };
        })()
        """
        data = await cdp.evaluate(sid, info_js) or {}
        
        inspected_results.append({
            "shortcode": code,
            "account": acc,
            "url": url,
            "views": c.get("views", 0),
            "views_str": views,
            "frame_path": frame_path,
            "caption": data.get("caption", "")
        })

    await cdp.close()
    
    out_path = "data/batch_inspected_top15.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(inspected_results, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Saved {len(inspected_results)} inspected reels to {out_path}")

if __name__ == "__main__":
    asyncio.run(inspect_pool())
