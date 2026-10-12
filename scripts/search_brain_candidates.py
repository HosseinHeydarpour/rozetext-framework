import os
import re
import json
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

already_selected = {
    "DNtMbWm0P4y", "DNTYt15oqYj", "DZDRxCkNgjw", "DbQ5ACmslaO", 
    "DPjl0mTCIps", "DO_homTiPTp", "DMqPqQCIem7", "DbyY0F7tmAn", "DPRj9ddCF5T"
}
existing_codes.update(already_selected)

brain_dir = r"C:\Users\User\.gemini\antigravity\brain"
reel_pattern = re.compile(r'https?://(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)/?', re.IGNORECASE)

candidates = {}

for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f.endswith(('.md', '.txt', '.json', '.jsonl')) and 'transcript' not in f and 'scripts-db' not in f:
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    text = fp.read()
            except Exception:
                continue
                
            for m in reel_pattern.finditer(text):
                code = m.group(1)
                if code in existing_codes or code in candidates:
                    continue
                    
                # Search window
                start = max(0, m.start() - 400)
                end = min(len(text), m.end() + 1500)
                window = text[start:end]
                
                # Check for 1M+ views
                has_1m = False
                view_str = ""
                for vm in re.finditer(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', window, re.IGNORECASE):
                    val = vm.group(1)
                    if '0.' not in val:
                        has_1m = True
                        view_str = val
                        break
                        
                if has_1m:
                    candidates[code] = {
                        "code": code,
                        "views": view_str,
                        "file": f,
                        "window": window
                    }

print(f"Total unique 1M+ candidates in brain: {len(candidates)}")
for c, info in candidates.items():
    print(f"[{c}] Views: {info['views']} | Source: {info['file']}")
