import json
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
scratch_dir = os.path.join(BASE_DIR, "scratch")
if scratch_dir not in sys.path:
    sys.path.insert(0, scratch_dir)

sys.stdout.reconfigure(encoding='utf-8')
from server import ENGINE
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")

with open(DB_PATH, "r", encoding="utf-8") as f:
    db = json.load(f)

existing_codes = set()
existing_hooks = set()
for s in db.get("scripts", []):
    u = s.get("source_url", "")
    if u:
        code = u.strip().rstrip("/").split("/")[-1]
        existing_codes.add(code)
    c = s.get("extracted_raw_text") or s.get("content") or ""
    lines = [l.strip() for l in c.splitlines() if l.strip()]
    if lines:
        existing_hooks.add(lines[0])

print(f"Existing DB shortcodes: {len(existing_codes)}")

files_to_check = [
    os.path.join(BASE_DIR, "data", "hunted-42-reels-batch-verified.json"),
    os.path.join(BASE_DIR, "data", "hunted-42-reels-batch.json"),
    os.path.join(BASE_DIR, "data", "hunted-batch-2026-09-29-4days.json"),
    os.path.join(BASE_DIR, "scratch", "test_pool.py")
]

candidates = {}

for fpath in files_to_check:
    if not os.path.exists(fpath):
        continue
    if fpath.endswith(".json"):
        with open(fpath, "r", encoding="utf-8") as f:
            items = json.load(f)
    elif fpath.endswith(".py"):
        # Let's import or parse
        try:
            import test_pool
            items = test_pool.pool + test_pool.verified_additional
        except Exception as e:
            print("Failed loading test_pool:", e)
            items = []
            
    for item in items:
        if not isinstance(item, dict):
            continue
        u = item.get("source_url", "")
        if not u:
            continue
        code = u.strip().rstrip("/").split("/")[-1]
        if code in existing_codes or code in candidates:
            continue
            
        views = str(item.get("source_views", ""))
        txt = item.get("extracted_raw_text") or item.get("content") or ""
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        
        # Check duplicate against published history
        dup = ENGINE.check_duplicate_against_history(txt, txt)
        if dup["is_duplicate"]:
            continue
            
        # Check duplicate against unpublished scripts in DB
        db_dup = False
        for s in db.get("scripts", []):
            s_txt = s.get("extracted_raw_text") or s.get("content") or ""
            # Check 4-gram or overlap
            check = ENGINE.check_duplicate_against_history(txt, s_txt)
            if check["is_duplicate"]:
                db_dup = True
                break
        if db_dup:
            continue
            
        # Check views >= 1M
        is_1m = ("M" in views or "میلیون" in views or "10," in views) and not ("0." in views)
        if not is_1m:
            continue
            
        # Check line count 7..16
        if len(lines) < 7 or len(lines) > 16:
            continue
            
        # Check caption trap
        is_caption_trap = any(kw in txt for kw in ["نظرتون رفقا", "شما هم", "برام بنویسید", "کامنت کنید", "ادامه در کپشن"])
        if is_caption_trap:
            continue
            
        candidates[code] = item

print(f"Total eligible 1M+ candidates found: {len(candidates)}")
for c, item in candidates.items():
    txt = item.get("extracted_raw_text") or item.get("content") or ""
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    print(f"[{c}] Views: {item.get('source_views')} | Lines: {len(lines)} | Page: {item.get('source_page')} | Hook: {lines[0][:35]}")
