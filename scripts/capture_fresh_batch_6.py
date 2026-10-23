import asyncio
import sys, os, json, base64
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

targets = [
    ("Ddmz-WgRM4K", "1.6M", "@___yeharf"),
    ("DdcA1OVC3dg", "2.0M", "@___yeharf"),
    ("C92muGvCeQU", "12.6M", "@heliumm.__"),
    ("Dd9GQ7HsdZM", "1.4M", "@text.love400"),
    ("DdmWLKdOUV0", "852K", "@text.love400"),
    ("DdYw7Mhu6m_", "846K", "@text.love400"),
]

async def capture_batch():
    cdp = ChromeCDP()
    await cdp.connect()
    t_list = await cdp.list_targets()
    ig = [t for t in t_list if 'instagram.com' in t.get('url', '')][0]
    sid = await cdp.attach_page(ig['targetId'])
    
    for code, views, page in targets:
        url = f"https://www.instagram.com/reel/{code}/"
        print(f"Navigating to {url} ({views})...")
        await cdp.navigate(sid, url)
        await asyncio.sleep(4)
        
        info = await cdp.evaluate(sid, """(() => {
            let v = document.querySelector('video');
            if (!v) return {found: false};
            v.pause(); v.currentTime = 2.0;
            let rect = v.getBoundingClientRect();
            return {found: true, x: rect.x, y: rect.y, width: rect.width, height: rect.height};
        })()""")
        
        if info.get("found"):
            clip = {'x': max(0, info['x']), 'y': max(0, info['y']), 'width': max(100, info['width']), 'height': max(100, info['height']), 'scale': 1}
            res = await cdp.send_cmd('Page.captureScreenshot', {'format': 'png', 'clip': clip}, session_id=sid)
            out_file = f"downloads/frames/{code}_2s.png"
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(res['data']))
            print(f"  -> Saved frame: {out_file}")
            
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(capture_batch())
