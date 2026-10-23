import asyncio
import sys, os, json
import websockets

def get_browser_ws():
    local_appdata = os.environ.get("LOCALAPPDATA")
    port_file = os.path.join(local_appdata, r"Google\Chrome\User Data\DevToolsActivePort")
    with open(port_file, "r") as f:
        port = f.readline().strip()
        path = f.readline().strip()
    return f"ws://127.0.0.1:{port}{path}"

async def inspect_account():
    ws_url = get_browser_ws()
    print("[1] Connecting to Chrome (Timeout: 60s - please click Allow if prompted)...")
    ws = await websockets.connect(ws_url, max_size=50 * 1024 * 1024, open_timeout=60)
    print("[2] Connected!")
    
    # 1. Target.getTargets
    payload = {"id": 1, "method": "Target.getTargets"}
    await ws.send(json.dumps(payload))
    res = json.loads(await ws.recv())
    targets = res.get("result", {}).get("targetInfos", [])
    ig = [t for t in targets if "instagram.com" in t.get("url", "")][0]
    
    # 2. Attach
    payload = {"id": 2, "method": "Target.attachToTarget", "params": {"targetId": ig["targetId"], "flatten": True}}
    await ws.send(json.dumps(payload))
    res = json.loads(await ws.recv())
    sid = res.get("result", {}).get("sessionId")
    
    # 3. Evaluate script to get logged in user info
    script = """
    (() => {
        // Look for links to profile
        let username = null;
        let links = Array.from(document.querySelectorAll('a'));
        for (let a of links) {
            let h = a.getAttribute('href') || '';
            // Check for profile icon / text
            if (a.querySelector('svg[aria-label="Profile"]') || 
                a.querySelector('svg[aria-label="پروفایل"]') ||
                (a.innerText || '').trim().toLowerCase() === 'profile' ||
                (a.innerText || '').trim() === 'پروفایل') {
                username = h.replace(/\\//g, '');
            }
        }
        
        // Also check if junkacc19982026 is present in document HTML
        let hasJunk = document.documentElement.innerHTML.includes('junkacc19982026');
        
        // ds_user_id cookie
        let m = document.cookie.match(/ds_user_id=([^;]+)/);
        let uid = m ? m[1] : null;

        return {
            detectedUsername: username,
            hasJunkacc: hasJunk,
            ds_user_id: uid,
            currentUrl: window.location.href,
            pageTitle: document.title
        };
    })()
    """
    payload = {
        "id": 3,
        "sessionId": sid,
        "method": "Runtime.evaluate",
        "params": {"expression": script, "returnByValue": True}
    }
    await ws.send(json.dumps(payload))
    res = json.loads(await ws.recv())
    data = res.get("result", {}).get("result", {}).get("value", {})
    print("\n--- ACCOUNT DETAILS ---")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    await ws.close()

if __name__ == "__main__":
    asyncio.run(inspect_account())
