import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine
from rozetext_scoring_engine_v3 import evaluate_script_v3

engine = AntiDuplicationEngine.get_instance()

async def inspect_candidates(candidates):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("[!] No IG tab")
        return []
        
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    results = []

    for idx, c in enumerate(candidates, 1):
        url = c["url"]
        views = c["views_str"]
        acc = c["account"]
        shortcode = c["shortcode"]
        print(f"\n[{idx}/{len(candidates)}] Inspecting {url} ({views} - {acc})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)

        # Pause at second 2
        pause_js = """
        (() => {
            let v = document.querySelector('video');
            if (v) {
                v.currentTime = 2.0;
                v.pause();
                return { dur: v.duration };
            }
            return null;
        })()
        """
        await cdp.evaluate(sid, pause_js)
        await asyncio.sleep(1.0)

        frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
        frame_path = os.path.join(frame_dir, f"{shortcode}_frame.png")
        await cdp.capture_screenshot(sid, frame_path)

        extract_js = """
        (() => {
            let spans = Array.from(document.querySelectorAll('article span, main span, div[dir="auto"]'))
                .map(s => s.innerText.trim())
                .filter(t => t.length > 5 && !t.includes('Follow') && !t.includes('Instagram'));
            
            let h1 = document.querySelector('h1');
            let caption = h1 ? h1.innerText : '';
            return { spans: spans.slice(0, 30), caption: caption };
        })()
        """
        data = await cdp.evaluate(sid, extract_js) or {}
        
        results.append({
            "account": acc,
            "url": url,
            "shortcode": shortcode,
            "views_str": views,
            "views": c.get("views", 0),
            "frame_path": frame_path,
            "caption": data.get("caption", ""),
            "spans": data.get("spans", [])
        })

    await cdp.close()
    out_file = "data/inspected_top_live_candidates.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Inspected {len(results)} reels! Saved to {out_file}")
    return results

if __name__ == "__main__":
    pool = json.load(open("data/fresh_live_hunted_pool.json", encoding="utf-8"))
    # Pick top 8 highest views
    top_candidates = sorted(pool, key=lambda x: x.get("views", 0), reverse=True)[:8]
    asyncio.run(inspect_candidates(top_candidates))
