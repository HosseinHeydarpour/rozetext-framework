import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,fa;q=0.8"
}

test_ids = ["DbbPmLFNZbj", "DZDRxCkNgjw", "DbQ5ACmslaO", "DbyY0F7tmAn", "DFQdHbroYkK", "DFItKaKI-VS", "DE2rzgOoJVJ", "DDclLBvIrOw", "DDKlRLZo_vt", "DCuQvWixK-A"]

for rid in test_ids:
    url = f"https://www.instagram.com/reel/{rid}/"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode("utf-8", errors="ignore")
            m_title = re.search(r'<meta property="og:title" content="([^"]+)"', html)
            m_desc = re.search(r'<meta property="og:description" content="([^"]+)"', html)
            title = m_title.group(1) if m_title else ""
            desc = m_desc.group(1) if m_desc else ""
            print(f"[{rid}] Title: {title[:60]} | Desc: {desc[:60]}")
    except Exception as e:
        print(f"[{rid}] Error: {e}")
