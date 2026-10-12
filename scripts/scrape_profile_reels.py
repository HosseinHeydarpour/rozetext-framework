import asyncio
import json
import os
import sys
import websockets

sys.stdout.reconfigure(encoding='utf-8')

async def scrape_profile(ws, session_id, username):
    url = f"https://www.instagram.com/{username}/reels/"
    print(f"\nNavigating to {url}...")
    await ws.send(json.dumps({"id": 10, "sessionId": session_id, "method": "Page.navigate", "params": {"url": url}}))
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == 10: break
    await asyncio.sleep(6.0)
    
    # Scroll down 3 times to load more reels
    for s in range(3):
        scroll_script = "window.scrollBy(0, 1500);"
        await ws.send(json.dumps({"id": 20+s, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": scroll_script}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 20+s: break
        await asyncio.sleep(2.5)
        
    extract_script = """
    (() => {
        const links = Array.from(document.querySelectorAll('a[href*="/reel/"], a[href*="/reels/"]'));
        const results = [];
        const seen = new Set();
        
        for (const a of links) {
            const href = a.href;
            const match = href.match(/reel[s]?\\/([^\\/]+)/);
            if (!match) continue;
            const code = match[1];
            if (seen.has(code)) continue;
            seen.add(code);
            
            // Look for view count inside link or parent
            const text = a.innerText || '';
            const spans = Array.from(a.querySelectorAll('span, div')).map(s => s.innerText.trim()).filter(Boolean);
            
            results.push({
                code: code,
                url: `https://www.instagram.com/reel/${code}/`,
                text: text,
                spans: spans.slice(0, 5)
            });
        }
        return results;
    })()
    """
    await ws.send(json.dumps({"id": 50, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": extract_script, "returnByValue": True}}))
    reels = []
    while True:
        msg = json.loads(await ws.recv())
        if msg.get("id") == 50:
            reels = msg.get("result", {}).get("result", {}).get("value", [])
            break
            
    print(f"Found {len(reels)} reels for {username}")
    for r in reels:
        print(f"  [{r['code']}] text: {repr(r['text'])} spans: {r['spans']}")
    return reels

async def main():
    port_file = r"C:\Users\User\AppData\Local\Google\Chrome\User Data\DevToolsActivePort"
    with open(port_file, "r", encoding="utf-8") as f:
        port = f.readline().strip()
        browser_path = f.readline().strip()
    ws_url = f"ws://127.0.0.1:{port}{browser_path}"
    async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.getTargets"}))
        targets = json.loads(await ws.recv()).get("result", {}).get("targetInfos", [])
        target_id = None
        for t in targets:
            if "(9+)" in t.get("title", "") or "EC0B4236635E918AC4B1C440773F5D7B" == t.get("targetId"):
                target_id = t["targetId"]
                break
        await ws.send(json.dumps({"id": 2, "method": "Target.attachToTarget", "params": {"targetId": target_id, "flatten": True}}))
        session_id = None
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 2: session_id = msg.get("result", {}).get("sessionId"); break
            elif msg.get("method") == "Target.attachedToTarget": session_id = msg.get("params", {}).get("sessionId"); break
            
        await scrape_profile(ws, session_id, "texthayedeli.ir")
        await scrape_profile(ws, session_id, "heliumm.__")

if __name__ == "__main__":
    asyncio.run(main())
