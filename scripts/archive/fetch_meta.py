import urllib.request
import re
import sys
import html

sys.stdout.reconfigure(encoding='utf-8')

candidates = [
    ("DZDRxCkNgjw", "1.5M", "https://www.instagram.com/reel/DZDRxCkNgjw/"),
    ("DbQ5ACmslaO", "1.3M", "https://www.instagram.com/reel/DbQ5ACmslaO/"),
    ("DFQdHbroYkK", "1.6M", "https://www.instagram.com/reel/DFQdHbroYkK/"),
    ("DFItKaKI-VS", "1.7M", "https://www.instagram.com/reel/DFItKaKI-VS/"),
    ("DE2rzgOoJVJ", "1.2M", "https://www.instagram.com/reel/DE2rzgOoJVJ/"),
    ("DDclLBvIrOw", "1.4M", "https://www.instagram.com/reel/DDclLBvIrOw/"),
    ("DDKlRLZo_vt", "1.5M", "https://www.instagram.com/reel/DDKlRLZo_vt/"),
    ("DCuQvWixK-A", "1.3M", "https://www.instagram.com/reel/DCuQvWixK-A/"),
    ("DbbPmLFNZbj", "1.8M", "https://www.instagram.com/reel/DbbPmLFNZbj/"),
]

for sc, views, url in candidates:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
        m = re.search(r'<meta (?:property|name)="og:description" content="(.*?)"', text)
        if not m:
            m = re.search(r'<meta (?:property|name)="description" content="(.*?)"', text)
        desc = html.unescape(m.group(1)) if m else ""
        print(f"=== {sc} ({views}) ===")
        # Clean likes prefix
        colon_idx = desc.find(': "')
        if colon_idx != -1:
            desc = desc[colon_idx + 3:]
        print(desc[:300].strip())
    except Exception as e:
        print(f"Error {sc}: {e}")
