import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

codes = ['DbGUEgZsr6E', 'Da7s8a7slWn', 'DacgLbesHkB', 'DcDeSnws_Yq', 'DdEeNFfs5V3', 'DakLbcdMUof', 'Da2YyLdsQMo']

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept-Language': 'fa,en-US;q=0.9,en;q=0.8'
}

for code in codes:
    url = f'https://www.instagram.com/reel/{code}/'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            og_t = re.search(r'<meta property="og:title" content="(.*?)"', html)
            og_d = re.search(r'<meta property="og:description" content="(.*?)"', html)
            print(f'=== {code} ===')
            if og_t:
                print('title:', og_t.group(1)[:150])
            if og_d:
                print('desc:', og_d.group(1)[:200])
    except Exception as e:
        print(f'=== {code} error: {e}')
