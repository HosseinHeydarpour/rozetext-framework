import asyncio
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine.get_instance()

async def inspect_reels(batch):
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig = [t for t in targets if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    frame_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "downloads", "frames")
    os.makedirs(frame_dir, exist_ok=True)
    
    results = []
    
    for idx, item in enumerate(batch, 1):
        url = item['url']
        shortcode = item['shortcode']
        acc = item['account']
        views = item['views_str']
        print(f"\n[{idx}/{len(batch)}] Inspecting {shortcode} ({acc} | {views})...")
        
        await cdp.navigate(sid, url)
        await asyncio.sleep(4.0)
        
        # Pause video at second 2.0
        pause_js = """
        (() => {
            let v = document.querySelector('video');
            if (v) {
                v.currentTime = 2.0;
                v.pause();
                return { dur: v.duration, w: v.videoWidth, h: v.videoHeight };
            }
            return null;
        })()
        """
        v_info = await cdp.evaluate(sid, pause_js)
        await asyncio.sleep(1.0)
        
        frame_path = os.path.join(frame_dir, f"{shortcode}_frame.png")
        await cdp.capture_screenshot(sid, frame_path)
        print(f"  Captured frame: {frame_path}")
        
        # Extract caption / title
        info_js = """
        (() => {
            let h1 = document.querySelector('h1');
            let caption = h1 ? h1.innerText.trim() : '';
            let spans = Array.from(document.querySelectorAll('article span, main span, div[dir="auto"]'))
                .map(s => s.innerText.trim())
                .filter(t => t.length > 5 && !t.includes('Follow') && !t.includes('Instagram'));
            return { caption: caption, spans: spans.slice(0, 15) };
        })()
        """
        data = await cdp.evaluate(sid, info_js) or {}
        caption = data.get('caption', '')
        
        results.append({
            'shortcode': shortcode,
            'account': acc,
            'url': url,
            'views': item['views'],
            'views_str': views,
            'frame_path': frame_path,
            'caption': caption,
            'spans': data.get('spans', [])
        })
        
    await cdp.close()
    out_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "inspected_fresh_subset.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(results)} inspected reels to {out_file}")

if __name__ == "__main__":
    with open("data/fresh_harvested_batch.json", "r", encoding="utf-8") as f:
        all_reels = json.load(f)
    
    # Target top candidates from khaazaan, text.love400, shadighorbanyy, ghalbe_daroon
    targets = [r for r in all_reels if r['account'] in ['@_khaazaan_', '@text.love400', '@shadighorbanyy', '@ghalbe_daroon', '@deep_dari9']]
    print(f"Found {len(targets)} targets to inspect")
    asyncio.run(inspect_reels(targets[:10]))
