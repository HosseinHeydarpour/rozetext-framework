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

target_files = [
    r"C:\Users\User\.gemini\antigravity\brain\98d0eba0-3dfb-436b-8672-42947d2825a2\.system_generated\logs\chunks\transcript_full_00000038.jsonl",
    r"C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\chunks\transcript_full_00000038.jsonl",
    r"C:\Users\User\.gemini\antigravity\brain\fbee23d0-df8d-41ce-83a6-d4fa1ebb241c\.system_generated\logs\chunks\transcript_full_00000038.jsonl"
]

candidates = []

for tf in target_files:
    if not os.path.exists(tf):
        continue
    with open(tf, "r", encoding="utf-8", errors="ignore") as fp:
        for line in fp:
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                # Look inside content or tool_calls
                text = json.dumps(obj, ensure_ascii=False)
                # Find all reel urls
                reels = re.findall(r'https?://(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)/?', text)
                for code in reels:
                    if code in existing_codes:
                        continue
                    # search around this code
                    idx = text.find(code)
                    window = text[max(0, idx-300):min(len(text), idx+1500)]
                    # check views
                    m_view = re.search(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', window)
                    if m_view and '0.' not in m_view.group(1):
                        candidates.append((code, m_view.group(1), tf, window))
            except Exception:
                pass

print(f"Total raw candidates found: {len(candidates)}")
unique_cands = {}
for code, view, tf, window in candidates:
    if code not in unique_cands and code not in existing_codes:
        unique_cands[code] = (view, tf, window)

print(f"Unique candidates: {len(unique_cands)}")
for code, (view, tf, window) in list(unique_cands.items())[:20]:
    print(f" - {code} | {view}")
