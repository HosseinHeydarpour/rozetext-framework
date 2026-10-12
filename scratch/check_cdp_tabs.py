import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    with urllib.request.urlopen('http://127.0.0.1:9222/json/list', timeout=3) as resp:
        tabs = json.loads(resp.read().decode('utf-8'))
        print(f"Total tabs: {len(tabs)}")
        for t in tabs:
            print(f"[{t.get('type')}] {t.get('title')} -> {t.get('url')}")
except Exception as e:
    print("Error:", e)
