import json, re, sys, os, html
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open(r'C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\candidates_32_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, it in enumerate(data):
    sc = it.get('shortcode')
    acc = it.get('account')
    v = it.get('views')
    cap = html.unescape(it.get('fullCaption') or '')
    print(f"[{i+1}] {sc} | @{acc} | {v}")
    # clean caption
    lines = [l.strip() for l in cap.splitlines() if l.strip()]
    for l in lines[:4]:
        print("   ", l)
