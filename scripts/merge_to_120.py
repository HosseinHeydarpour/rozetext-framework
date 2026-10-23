import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BENCHMARK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_accounts.json")
EXPANSION_30_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expansion_30_to_120_verified.json")

def merge():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        base_data = json.load(f)
        
    base_accounts = base_data.get("accounts", [])
    existing_handles = {a.get("handle", "").lower(): a for a in base_accounts}
    
    new_accounts = []
    if os.path.exists(EXPANSION_30_PATH):
        with open(EXPANSION_30_PATH, "r", encoding="utf-8") as f:
            exp_data = json.load(f)
        for item in exp_data:
            h_key = item.get("handle", "").lower()
            if h_key not in existing_handles and item.get("status") == "verified_live":
                new_accounts.append(item)
                existing_handles[h_key] = item
                
    combined = base_accounts + new_accounts
    print(f"Base: {len(base_accounts)} | New verified: {len(new_accounts)} | Total: {len(combined)}")
    
    base_data["meta"]["total_accounts"] = len(combined)
    base_data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    base_data["meta"]["status"] = f"verified_live_instagram_crawl_{len(combined)}_accounts"
    base_data["accounts"] = combined
    
    with open(BENCHMARK_PATH, "w", encoding="utf-8") as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(combined)} accounts to {BENCHMARK_PATH}")
    
    # Rebuild markdown directory
    os.system("python scripts/build_benchmark_registry.py")

if __name__ == "__main__":
    merge()
