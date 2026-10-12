import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}
url = 'https://www.instagram.com/reel/DHOoHu0IiOA/'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for meta tags
metas = re.findall(r'<meta [^>]+>', html)
for m in metas:
    if any(k in m for k in ['description', 'title', 'caption', 'caption_text']):
        print(m)

# Also check for JSON-LD or script tags with caption
scripts = re.findall(r'<script type="application/ld\+json">([^<]+)</script>', html)
for s in scripts:
    print("LD+JSON:", s[:500])
