import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def test_continuous():
    cdp = ChromeCDP()
    print("[1] Connecting...")
    await cdp.connect()
    print("[2] Connected!")
    
    targets = await cdp.list_targets()
    ig = [t for t in targets if "instagram.com" in t.get("url", "")][0]
    sid = await cdp.attach_page(ig["targetId"])
    
    print("[3] First eval (checking URL)...")
    url = await cdp.evaluate(sid, "window.location.href")
    print(f"   -> {url}")
    
    await asyncio.sleep(1)
    print("[4] Second eval on same socket (checking title)...")
    title = await cdp.evaluate(sid, "document.title")
    print(f"   -> {title}")
    
    await asyncio.sleep(1)
    print("[5] Third eval on same socket (checking innerWidth)...")
    w = await cdp.evaluate(sid, "window.innerWidth")
    print(f"   -> Window width: {w}")
    
    print("[6] Done without disconnecting!")
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(test_continuous())
