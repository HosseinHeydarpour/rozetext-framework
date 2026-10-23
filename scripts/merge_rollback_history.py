import json
import os
import shutil
from datetime import datetime

def rollback_and_merge():
    # 1. Load backup containing historical scripts
    bak_path = "data/scripts-db.json.bak"
    with open(bak_path, "r", encoding="utf-8") as f:
        bak_data = json.load(f)
    
    # 2. Load current db containing the 21 new verified scripts from Tuesday 2026-10-13
    curr_path = "data/scripts-db.json"
    with open(curr_path, "r", encoding="utf-8") as f:
        curr_data = json.load(f)
        
    # Extract historical scripts up to 2026-10-12
    historical_scripts = [
        s for s in bak_data.get("scripts", [])
        if (s.get("scheduled_date") or "") <= "2026-10-12"
    ]
    
    # Extract new verified scripts starting from 2026-10-13
    new_verified_scripts = [
        s for s in curr_data.get("scripts", [])
        if (s.get("scheduled_date") or "") >= "2026-10-13"
    ]
    
    print(f"[*] Restoring {len(historical_scripts)} historical scripts (<= 2026-10-12)...")
    print(f"[*] Preserving {len(new_verified_scripts)} newly hunted scripts (>= 2026-10-13)...")
    
    # Combine
    combined_scripts = historical_scripts + new_verified_scripts
    print(f"[+] Total merged scripts: {len(combined_scripts)}")
    
    # Check date coverage
    dates = {}
    for s in combined_scripts:
        dates.setdefault(s.get("scheduled_date"), []).append(s.get("scheduled_slot"))
        
    for d in sorted(dates.keys()):
        print(f"  - {d}: {len(dates[d])} scripts (slots {sorted(dates[d])})")
        
    # Meta preservation
    meta = bak_data.get("meta", {})
    meta["last_updated"] = datetime.now().isoformat()
    meta["base_history_count"] = 233
    
    final_db = {
        "meta": meta,
        "scripts": combined_scripts
    }
    
    # Backup current before overwriting
    os.makedirs("data/archive", exist_ok=True)
    shutil.copy(curr_path, "data/archive/scripts-db-pre-rollback.json")
    
    with open(curr_path, "w", encoding="utf-8") as f:
        json.dump(final_db, f, ensure_ascii=False, indent=2)
        
    print("[SUCCESS] data/scripts-db.json successfully merged and restored!")

if __name__ == "__main__":
    rollback_and_merge()
