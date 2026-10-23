import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.chrome_cdp import ChromeCDP

async def inspect_golden():
    reels = [
        # vahidrezakhoshbayan
        {"shortcode": "DbQ5ACmslaO", "acc": "@vahidrezakhoshbayan", "url": "https://www.instagram.com/vahidrezakhoshbayan/reel/DbQ5ACmslaO/", "views": "1.3M"},
        {"shortcode": "DaN7SayomTk", "acc": "@vahidrezakhoshbayan", "url": "https://www.instagram.com/vahidrezakhoshbayan/reel/DaN7SayomTk/", "views": "972K"},
        {"shortcode": "DZX3utUt9xI", "acc": "@vahidrezakhoshbayan", "url": "https://www.instagram.com/vahidrezakhoshbayan/reel/DZX3utUt9xI/", "views": "576K"},
        {"shortcode": "DZId7nxNc_K", "acc": "@vahidrezakhoshbayan", "url": "https://www.instagram.com/vahidrezakhoshbayan/reel/DZId7nxNc_K/", "views": "611K"},
        {"shortcode": "DS0LBApiHx1", "acc": "@vahidrezakhoshbayan", "url": "https://www.instagram.com/vahidrezakhoshbayan/reel/DS0LBApiHx1/", "views": "500K"},
        {"shortcode": "DSp5q5XiOlJ", "acc": "@vahidrezakhoshbayan", "url": "https://www.instagram.com/vahidrezakhoshbayan/reel/DSp5q5XiOlJ/", "views": "619K"},
        # text.love400
        {"shortcode": "DcoiLlvssrD", "acc": "@text.love400", "url": "https://www.instagram.com/text.love400/reel/DcoiLlvssrD/", "views": "1.1M"},
        {"shortcode": "DeTrPm0uZrh", "acc": "@text.love400", "url": "https://www.instagram.com/text.love400/reel/DeTrPm0uZrh/", "views": "699K"},
        {"shortcode": "DdmWLKdOUV0", "acc": "@text.love400", "url": "https://www.instagram.com/text.love400/reel/DdmWLKdOUV0/", "views": "908K"},
        {"shortcode": "DdPE-C_ODtV", "acc": "@text.love400", "url": "https://www.instagram.com/text.love400/reel/DdPE-C_ODtV/", "views": "1.2M"},
        # zahraa.nature
        {"shortcode": "Dc_z1QtMhd7", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/Dc_z1QtMhd7/", "views": "844K"},
        {"shortcode": "Dcy79eFObfp", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/Dcy79eFObfp/", "views": "555K"},
        {"shortcode": "DcLWPPZO0XW", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/DcLWPPZO0XW/", "views": "787K"},
        {"shortcode": "DblsFKUsRjn", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/DblsFKUsRjn/", "views": "720K"},
        {"shortcode": "DbjHTCAMKq8", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/DbjHTCAMKq8/", "views": "782K"},
        {"shortcode": "Dbd9tTKMOsp", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/Dbd9tTKMOsp/", "views": "751K"},
        {"shortcode": "DbbY_s-MMK0", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/DbbY_s-MMK0/", "views": "847K"},
        {"shortcode": "DbOwfqmMGk-", "acc": "@zahraa.nature", "url": "https://www.instagram.com/zahraa.nature/reel/DbOwfqmMGk-/", "views": "599K"},
        # leyli_geraphy & sepehr_kh
        {"shortcode": "DcZbpT3tOCV", "acc": "@leyli_geraphy", "url": "https://www.instagram.com/leyli_geraphy/reel/DcZbpT3tOCV/", "views": "993K"},
        {"shortcode": "DQCXo9fDMII", "acc": "@sepehr_kh", "url": "https://www.instagram.com/sepehr_kh/reel/DQCXo9fDMII/", "views": "1.1M"},
    ]

    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
    os.makedirs(frame_dir, exist_ok=True)
    
    inspected = []
    
    for idx, r in enumerate(reels, 1):
        code = r['shortcode']
        url = r['url']
        acc = r['acc']
        views = r['views']
        print(f"[{idx}/{len(reels)}] {code} ({acc} | {views})...")
        
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
        
        fpath = os.path.join(frame_dir, f"{code}_frame.png")
        await cdp.capture_screenshot(sid, fpath)
        print(f"  Frame: {fpath}")
        
        h1_js = "(() => { let h = document.querySelector('h1'); return h ? h.innerText.trim() : ''; })()"
        caption = await cdp.evaluate(sid, h1_js) or ""
        
        inspected.append({
            "shortcode": code,
            "account": acc,
            "url": url,
            "views_str": views,
            "frame_path": fpath,
            "caption": caption
        })

    await cdp.close()
    out = "data/golden_inspected_pool.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(inspected, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Saved {len(inspected)} frames to {out}")

if __name__ == "__main__":
    asyncio.run(inspect_golden())
