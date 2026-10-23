import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def run_simulation():
    cdp = ChromeCDP()
    print("[1] Connecting to Chrome WebSocket...")
    await cdp.connect()
    print("[2] Connected successfully!")
    
    targets = await cdp.list_targets()
    print(f"[3] Found {len(targets)} active targets.")
    
    ig_target = None
    for t in targets:
        url = t.get("url", "")
        if "instagram.com" in url:
            ig_target = t
            print(f"   -> Found Instagram target: {t['targetId']} ({url})")
            break
            
    if ig_target:
        print("[4] Attaching to Instagram page target without disconnecting...")
        sid = await cdp.attach_page(ig_target["targetId"])
        print(f"   -> Attached sessionId: {sid}")
        title = await cdp.evaluate(sid, "document.title")
        url = await cdp.evaluate(sid, "window.location.href")
        print(f"   -> Page Title: {title}")
        print(f"   -> Page URL: {url}")
        print("[5] Executing test DOM read...")
        video_count = await cdp.evaluate(sid, "document.querySelectorAll('video').length")
        print(f"   -> Videos currently in DOM: {video_count}")
        print("[SUCCESS] All steps executed seamlessly!")
    else:
        print("[-] No Instagram tab found among open tabs.")
        
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(run_simulation())
