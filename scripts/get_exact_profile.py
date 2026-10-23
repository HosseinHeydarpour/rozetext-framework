import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def get_exact_profile():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print(json.dumps({"error": "No Instagram tab"}))
        await cdp.close()
        return

    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    
    script = """
    (() => {
        // Look for the Profile link in sidebar
        let links = Array.from(document.querySelectorAll('a')).map(a => ({
            href: a.getAttribute('href'),
            text: (a.innerText || '').trim(),
            aria: a.getAttribute('aria-label') || ''
        }));
        
        // Find links that look like profile links
        let profileLinks = links.filter(l => l.href && l.href.startsWith('/') && l.text.toLowerCase().includes('profile'));
        if (profileLinks.length === 0) {
            // maybe in Persian 'پروفایل'
            profileLinks = links.filter(l => l.href && l.href.startsWith('/') && (l.text.includes('پروفایل') || l.aria.includes('پروفایل')));
        }
        
        // Also check window.__initialData or window._sharedData
        let configUser = null;
        try {
            if (window._sharedData && window._sharedData.config) {
                configUser = window._sharedData.config.viewer;
            }
        } catch(e) {}
        
        return {
            profileLinks: profileLinks,
            allLinksSample: links.slice(0, 20),
            configUser: configUser
        };
    })()
    """
    res = await cdp.evaluate(sid, script)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(get_exact_profile())
