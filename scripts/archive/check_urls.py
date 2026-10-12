import urllib.request
import re
import sys
import html

sys.stdout.reconfigure(encoding='utf-8')

test_urls = [
    ('DKC2DQwIyM_ (CORRECT)', 'https://www.instagram.com/reel/DKC2DQwIyM_/'),
    ('DKC2DqwiyM_ (TYPO)', 'https://www.instagram.com/reel/DKC2DqwiyM_/'),
    ('DMvWoiaor6o (CORRECT)', 'https://www.instagram.com/reel/DMvWoiaor6o/'),
    ('DKm6Qn6I9vQ (CORRECT)', 'https://www.instagram.com/reel/DKm6Qn6I9vQ/')
]

for label, url in test_urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('utf-8', errors='ignore')
        m = re.search(r'<meta (?:property|name)="og:description" content="(.*?)"', text)
        desc = html.unescape(m.group(1)) if m else 'No meta'
        print(f'{label} [Status {resp.status}]: {desc[:120]}...')
    except Exception as e:
        print(f'{label} FAILED: {e}')
