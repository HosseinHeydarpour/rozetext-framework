import asyncio
import sys, os, json, base64, time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

async def inspect_candidates_slice(start_idx=12, max_to_capture=15):
    candidates = json.load(open('data/hashtag_candidates.json', encoding='utf-8'))
    db = json.load(open('data/scripts-db.json', encoding='utf-8'))
    db_urls = {s.get('source_url') for s in db['scripts'] if s.get('source_url')}
    
    cdp = ChromeCDP()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Chrome (Patient loop - please click Allow if prompted)...")
    while True:
        try:
            await cdp.connect()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected successfully!")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for Allow click in Chrome... ({e})")
            await asyncio.sleep(3)
    
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '') or 'Instagram' in t.get('title', '')]
    if not ig_targets:
        print("No IG target found!")
        await cdp.close()
        return
        
    sid = await cdp.attach_page(ig_targets[0]['targetId'])
    os.makedirs("downloads/frames", exist_ok=True)
    
    # Load previously captured list to append
    captured_file = 'data/hashtag_captured_reels.json'
    if os.path.exists(captured_file):
        captured_reels = json.load(open(captured_file, encoding='utf-8'))
    else:
        captured_reels = []
    
    captured_urls = {c['url'] for c in captured_reels}
    
    start_time = time.time()
    last_report_time = time.time()
    newly_captured = 0
    
    print(f"Starting inspection from index {start_idx} of {len(candidates)} candidates...")
    
    for i in range(start_idx, len(candidates)):
        now = time.time()
        if now - last_report_time >= 300: # 5 min
            last_report_time = now
            elapsed = int((now - start_time) / 60)
            print(f"\n>>> [5-MIN INTERVAL | {datetime.now().strftime('%H:%M:%S')}] Elapsed: {elapsed}m | Inspected idx: {i}/{len(candidates)} | New Captured: {newly_captured} <<<\n")
            
        c = candidates[i]
        u = c['url']
        sc = c['shortcode']
        tag = c['tag']
        
        if u in db_urls or u in captured_urls:
            continue
            
        print(f"[{i+1}/{len(candidates)}] Navigating to: {u} (#{tag})...")
        try:
            await cdp.navigate(sid, u)
            await asyncio.sleep(3.5)
            
            script = """
            (() => {
                let v = document.querySelector('video');
                if (!v) return {isVideo: false};
                
                // Look for view count
                let views = '';
                let spans = Array.from(document.querySelectorAll('span, a')).map(s => s.innerText.trim());
                for (let s of spans) {
                    if (s.includes('plays') || s.includes('views') || s.includes('بازدید')) {
                        views = s;
                        break;
                    }
                }
                
                // Look for likes
                let likes = '';
                let likeSpan = Array.from(document.querySelectorAll('span')).find(s => s.innerText.includes('others') || s.innerText.includes('نفر'));
                if (likeSpan) likes = likeSpan.innerText;

                // Get account username from header or links
                let userEl = document.querySelector('header a') || document.querySelector('div[class*="x1i10hfl"] a');
                let username = userEl ? userEl.innerText.trim() : '';

                v.pause();
                v.currentTime = 2.0;
                let rect = v.getBoundingClientRect();
                
                return {
                    isVideo: true,
                    duration: v.duration,
                    views: views,
                    likes: likes,
                    username: username,
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height
                };
            })()
            """
            info = await cdp.evaluate(sid, script)
            if not info or not info.get('isVideo'):
                print("  -> Not a video.")
                continue
                
            print(f"  -> VIDEO: @{info.get('username')} | views: {info.get('views')} | likes: {info.get('likes')}")
            
            # Capture frame
            clip = {'x': max(0, info['x']), 'y': max(0, info['y']), 'width': max(100, info['width']), 'height': max(100, info['height']), 'scale': 1}
            res = await cdp.send_cmd('Page.captureScreenshot', {'format': 'png', 'clip': clip}, session_id=sid)
            frame_path = f"downloads/frames/{sc}_tag.png"
            with open(frame_path, 'wb') as f:
                f.write(base64.b64decode(res['data']))
                
            item = {
                "shortcode": sc,
                "url": u,
                "tag": tag,
                "account": f"@{info.get('username')}",
                "views": info.get('views'),
                "likes": info.get('likes'),
                "frame_path": frame_path
            }
            captured_reels.append(item)
            captured_urls.add(u)
            newly_captured += 1
            
            # Save progress continually
            with open(captured_file, 'w', encoding='utf-8') as f:
                json.dump(captured_reels, f, ensure_ascii=False, indent=2)
                
            if newly_captured >= max_to_capture:
                print(f"Reached capture quota of {max_to_capture} new video reels!")
                break
        except Exception as err:
            print(f"  -> Error inspecting {sc}: {err}")
            await asyncio.sleep(2)
            
    print(f"\n[DONE] Finished inspection slice! Total newly captured: {newly_captured} (Grand total: {len(captured_reels)})")
    await cdp.close()

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    max_c = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    asyncio.run(inspect_candidates_slice(start, max_c))
