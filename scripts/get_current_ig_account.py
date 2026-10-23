import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def get_account_info():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print(json.dumps({"error": "No Instagram tab found"}))
        await cdp.close()
        return

    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    
    # Extract logged in user info from DOM / local storage / window
    script = """
    (() => {
        let username = null;
        let name = null;
        
        // 1. Try finding profile link in sidebar / navigation
        const profileLinks = Array.from(document.querySelectorAll('a[href^="/"]')).filter(a => {
            const h = a.getAttribute('href');
            return h && !['/', '/explore/', '/reels/', '/direct/inbox/', '/notifications/'].includes(h) && 
                   !h.includes('/stories/') && !h.includes('/p/') && !h.includes('/reel/') && !h.startsWith('/accounts/');
        });
        
        // Check aria-labels or text or profile icons
        for (const a of document.querySelectorAll('a')) {
            const href = a.getAttribute('href') || '';
            const text = (a.innerText || '').trim();
            const aria = a.getAttribute('aria-label') || '';
            if (href.length > 2 && href.startsWith('/') && !href.slice(1).includes('/') && href.slice(1).length > 2) {
                // Potential profile link
                const span = a.querySelector('span');
                if (span && span.innerText.trim() === 'Profile') {
                    username = href.replace(/\\//g, '');
                }
            }
        }
        
        // Try _sharedData or cookie ds_user_id
        const cookies = document.cookie;
        const ds_user_match = cookies.match(/ds_user_id=([^;]+)/);
        const ds_user_id = ds_user_match ? ds_user_match[1] : null;

        // Try title or url
        const title = document.title;
        const currentUrl = window.location.href;
        
        // Also look for profile avatar
        const img = document.querySelector('img[data-testid="user-avatar"]') || 
                    document.querySelector('header img') || 
                    document.querySelector('nav img');
        const avatar = img ? img.src : null;

        return {
            username: username,
            ds_user_id: ds_user_id,
            title: title,
            currentUrl: currentUrl,
            avatar: avatar
        };
    })()
    """
    info = await cdp.evaluate(sid, script)
    print(json.dumps(info, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(get_account_info())
