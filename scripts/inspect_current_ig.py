import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def main():
    cdp = ChromeCDP()
    await cdp.connect()
    sid = await cdp.attach_page('DD1DF7845B8CDAC41D5884C86D74F67F')
    js = """
    (() => {
        const url = window.location.href;
        const links = Array.from(document.querySelectorAll('a[role="link"], a[href*="/reel/"], a[href^="/"]')).map(a => ({
            href: a.getAttribute('href'),
            text: a.innerText.trim()
        })).filter(x => x.text || x.href);
        const videos = Array.from(document.querySelectorAll('video')).map(v => ({
            src: v.src,
            paused: v.paused,
            currentTime: v.currentTime,
            duration: v.duration
        }));
        const captions = Array.from(document.querySelectorAll('h1, span._ap3a, div._a9zs')).map(el => el.innerText.trim()).filter(Boolean);
        return {
            url: url,
            links: links.slice(0, 20),
            videos: videos,
            captions: captions.slice(0, 10)
        };
    })()
    """
    res = await cdp.evaluate(sid, js)
    sys.stdout.reconfigure(encoding='utf-8')
    with open('data/current_ig_inspect.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("Saved inspection to data/current_ig_inspect.json")
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(main())
