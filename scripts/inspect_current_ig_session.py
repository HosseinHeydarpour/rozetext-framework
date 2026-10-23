import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from chrome_cdp import ChromeCDP

async def inspect():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com/?hl=en' in t.get('url', '') or '(9+) Instagram' in t.get('title', '')]
    if not ig_targets:
        ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '')]
    if not ig_targets:
        print(json.dumps({"error": "No IG targets"}))
        await cdp.close()
        return

    target = ig_targets[0]
    sid = await cdp.attach_page(target['targetId'])

    js_code = """
    (() => {
        let username = null;
        let profileHref = null;
        const anchors = Array.from(document.querySelectorAll('a'));
        for (const a of anchors) {
            const h = a.getAttribute('href') || '';
            const text = (a.innerText || '').toLowerCase();
            if (text.includes('profile') || a.querySelector('img[alt*="profile"]')) {
                username = h.replace(/\\//g, '');
                profileHref = h;
                break;
            }
        }
        
        let ds = document.cookie.match(/ds_user_id=([^;]+)/);
        return {
            targetTitle: document.title,
            currentUrl: window.location.href,
            username: username,
            profileHref: profileHref,
            ds_user_id: ds ? ds[1] : null
        };
    })()
    """
    res = await cdp.evaluate(sid, js_code)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(inspect())
