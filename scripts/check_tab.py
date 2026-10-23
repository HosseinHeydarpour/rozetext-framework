import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def main():
    cdp = ChromeCDP()
    await cdp.connect()
    sid = await cdp.attach_page('DD1DF7845B8CDAC41D5884C86D74F67F')
    url = await cdp.evaluate(sid, 'window.location.href')
    title = await cdp.evaluate(sid, 'document.title')
    print(f"URL: {url}", flush=True)
    print(f"Title: {title}", flush=True)
    await cdp.close()

if __name__ == "__main__":
    asyncio.run(main())
