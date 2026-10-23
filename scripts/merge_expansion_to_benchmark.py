import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

BENCHMARK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_accounts.json")
EXPANSION_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expansion_candidates_verified.json")
EXTRA_4_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "extra_4_verified.json")
AUDIT_RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_audit_results.json")

def merge():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        base_data = json.load(f)
        
    base_accounts = base_data.get("accounts", [])
    existing_handles = {a.get("handle", "").lower(): a for a in base_accounts}
    
    # Update base accounts with live audited follower data if available
    if os.path.exists(AUDIT_RESULTS_PATH):
        try:
            with open(AUDIT_RESULTS_PATH, "r", encoding="utf-8") as f:
                audit = json.load(f)
            verified = audit.get("verified_accounts", {})
            for h, info in verified.items():
                handle_key = f"@{h}".lower()
                if handle_key in existing_handles:
                    if info.get("followers_detected"):
                        existing_handles[handle_key]["followers"] = f"{info['followers_detected']} (Verified Live)"
        except Exception as e:
            print(f"Warning updating followers from audit: {e}")
            
    # Load expansion accounts (32 accounts)
    new_accounts = []
    for file_path in [EXPANSION_PATH, EXTRA_4_PATH]:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
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
    base_data["meta"]["status"] = "verified_live_instagram_crawl_90_accounts"
    base_data["accounts"] = combined
    
    with open(BENCHMARK_PATH, "w", encoding="utf-8") as f:
        json.dump(base_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(combined)} accounts to {BENCHMARK_PATH}")
    
    # Run build_benchmark_registry to update markdown
    os.system("python scripts/build_benchmark_registry.py")

if __name__ == "__main__":
    merge()
