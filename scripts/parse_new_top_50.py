import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
p = r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\new_top_50_reels.json"
raw = open(p, encoding='utf-8').read()
d = json.loads(json.loads(raw))
print(f"Decoded {len(d)} items from new_top_50_reels.json:")
for i, item in enumerate(d):
    sc = item.get("shortcode")
    v = item.get("views")
    acc = item.get("account")
    txt = item.get("text", "").replace("\n", " ")
    print(f"[{i}] {sc} | {acc} | {v} | {txt[:60]}")
