import asyncio
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def batch_capture(limit=40):
    all_reels = json.load(open('data/all_harvested_ranked.json', encoding='utf-8'))
    
    # Filter reels: >= 200k views, or high views
    candidates = [r for r in all_reels if r['views'] >= 150_000]
    print(f"Total candidates with >= 150k views: {len(candidates)}")
    
    cdp = ChromeCDP()
    await cdp.connect()
    sid = await cdp.attach_page('DD1DF7845B8CDAC41D5884C86D74F67F')
    
    os.makedirs("artifacts/reels_screenshots", exist_ok=True)
    captured = []
    
    for idx, r in enumerate(candidates[:limit]):
        code = r['shortcode']
        shot_path = f"artifacts/reels_screenshots/{code}.png"
        if os.path.exists(shot_path) and os.path.getsize(shot_path) > 10000:
            print(f"[{idx+1}/{limit}] Already captured {code}")
            captured.append((r, shot_path))
            continue
            
        url = r['url']
        print(f"[{idx+1}/{limit}] Capturing {code} ({r['views_str']} - @{r['account']})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(3.5)
        
        try:
            await cdp.capture_screenshot(sid, shot_path)
            captured.append((r, shot_path))
        except Exception as e:
            print(f"Error capturing {code}: {e}")
            
    await cdp.close()
    print(f"Done. Captured {len(captured)} reels.")

if __name__ == "__main__":
    asyncio.run(batch_capture(40))
