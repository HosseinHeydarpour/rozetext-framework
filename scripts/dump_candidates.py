import json
import re
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

path = r"C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\chunks\transcript_full\00000038.jsonl"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target_codes = ["DJeyrN9oAxI", "DMVWoiaor6o", "DKm6Qn6I9VQ", "DLvAFwdo67j", "DFK4s89or6Z"]

for c in target_codes:
    print(f"\n==================== CODE: {c} ====================")
    idx = text.find(c)
    if idx != -1:
        start = max(0, idx - 400)
        end = min(len(text), idx + 2000)
        snippet = text[start:end]
        print(snippet[:1500])
