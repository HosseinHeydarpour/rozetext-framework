import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def check_storage():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    
    script = """
    (() => {
        let keys = Object.keys(localStorage);
        let userKeys = {};
        for (let k of keys) {
            if (k.toLowerCase().includes('user') || k.toLowerCase().includes('session') || k.toLowerCase().includes('profile')) {
                userKeys[k] = localStorage.getItem(k).slice(0, 200);
            }
        }
        return {
            totalKeys: keys.length,
            userKeys: userKeys
        };
    })()
    """
    res = await cdp.evaluate(sid, script)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(check_storage())
