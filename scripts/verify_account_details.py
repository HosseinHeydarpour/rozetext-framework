import asyncio
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def get_profile_stats():
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print(json.dumps({"error": "No Instagram tab"}))
        return

    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    
    # Navigate to user's profile
    await cdp.navigate(sid, "https://www.instagram.com/hosseinheydarpour/")
    await asyncio.sleep(3.5)
    
    js = """
    (() => {
        let fullName = null;
        let bio = null;
        let posts = "0";
        let followers = "0";
        let following = "0";
        
        let header = document.querySelector('header');
        if (header) {
            let spans = Array.from(header.querySelectorAll('span, h1, h2')).map(s => s.innerText.trim()).filter(Boolean);
            
            // Look for follower counts in list items
            let listItems = Array.from(header.querySelectorAll('li'));
            for (let li of listItems) {
                let txt = li.innerText;
                if (txt.includes('post') || txt.includes('پست')) posts = txt;
                if (txt.includes('follower') || txt.includes('دنبال‌کننده')) followers = txt;
                if (txt.includes('following') || txt.includes('دنبال‌شده')) following = txt;
            }
            
            let h1 = header.querySelector('h1') || header.querySelector('h2');
            fullName = h1 ? h1.innerText : '';
        }

        return {
            username: "hosseinheydarpour",
            fullName: fullName,
            uid: "74239395220",
            posts: posts,
            followers: followers,
            following: following,
            is_empty_or_secondary: true
        };
    })()
    """
    res = await cdp.evaluate(sid, js)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(get_profile_stats())
