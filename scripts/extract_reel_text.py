import asyncio
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

async def get_persian_texts():
    cdp = ChromeCDP()
    await cdp.connect()
    sid = await cdp.attach_page('DD1DF7845B8CDAC41D5884C86D74F67F')
    
    js = """
    (() => {
        const persianRegex = /[\u0600-\u06FF]/;
        const allElements = Array.from(document.querySelectorAll('*'));
        const persianTexts = [];
        for (const el of allElements) {
            if (el.children.length === 0 && persianRegex.test(el.innerText || '')) {
                const txt = el.innerText.trim();
                if (txt && !persianTexts.includes(txt)) {
                    persianTexts.push(txt);
                }
            }
        }
        return persianTexts;
    })()
    """
    res = await cdp.evaluate(sid, js)
    await cdp.close()
    return res

if __name__ == "__main__":
    texts = asyncio.run(get_persian_texts())
    with open("data/persian_extracted.json", "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(texts)} Persian text elements. Saved to data/persian_extracted.json")
