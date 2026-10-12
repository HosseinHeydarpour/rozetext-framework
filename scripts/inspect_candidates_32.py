import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
sys.stdout.reconfigure(encoding='utf-8')

from server import ENGINE

DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")
with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

existing_codes = set()
for s in db.get("scripts", []):
    u = s.get("source_url", "")
    if u:
        existing_codes.add(u.strip().rstrip("/").split("/")[-1])

already_chosen = {
    "DNtMbWm0P4y", "DNTYt15oqYj", "DZDRxCkNgjw", "DbQ5ACmslaO", 
    "DPjl0mTCIps", "DO_homTiPTp", "DMqPqQCIem7", "DbyY0F7tmAn", "DPRj9ddCF5T"
}
existing_codes.update(already_chosen)

path = r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\candidates_32_data.json"
with open(path, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total items in candidates_32_data: {len(items)}")
for it in items:
    sc = it.get("shortcode")
    acc = it.get("account")
    v = str(it.get("views"))
    desc = it.get("ogDesc", "").replace("\n", " ")
    in_db = sc in existing_codes
    is_1m = ("M" in v or "میلیون" in v or "10," in v) and not ("0." in v)
    if is_1m and not in_db:
        print(f"Candidate: {sc} | {acc} | Views: {v} | Desc: {desc[:50]}")
