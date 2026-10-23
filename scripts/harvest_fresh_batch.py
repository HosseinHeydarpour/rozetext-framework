import asyncio
import base64
import json
import os
import random
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP

BENCHMARK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_accounts.json")
ROTATION_STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "hunting_rotation_state.json")

def load_benchmark_directory():
    if not os.path.exists(BENCHMARK_PATH):
        return [], {}
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    accounts = data.get("accounts", [])
    acc_map = {a.get("handle", "").replace("@", "").strip().lower(): a for a in accounts}
    handles = [a.get("handle", "").replace("@", "").strip() for a in accounts]
    return handles, acc_map

def get_adaptive_floor(account_handle, accounts_map):
    meta = accounts_map.get(account_handle.lower(), {})
    followers_str = str(meta.get("followers", "")).lower()
    
    # Check for M (millions)
    if "m" in followers_str:
        return 350000
        
    m_k = re.search(r"(\d+(?:\.\d+)?)\s*k", followers_str)
    if m_k:
        try:
            k_val = float(m_k.group(1))
            if k_val >= 500:
                return 300000
            elif k_val >= 100:
                return 220000
            else:
                return 150000
        except Exception:
            pass
            
    # Default floor for smaller/specialized accounts
    return 180000

def get_next_accounts_batch(batch_size=8):
    all_accounts, _ = load_benchmark_directory()
    if not all_accounts:
        all_accounts = ["___yeharf", "atiya_text", "heliumm.__", "docharetooo", "text.love400"]
    
    state = {}
    if os.path.exists(ROTATION_STATE_PATH):
        try:
            with open(ROTATION_STATE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            state = {}
            
    last_index = state.get("last_index", 0)
    total = len(all_accounts)
    if total == 0:
        return []
        
    start_idx = last_index % total
    batch = []
    for i in range(batch_size):
        idx = (start_idx + i) % total
        batch.append(all_accounts[idx])
        
    new_index = (start_idx + batch_size) % total
    state["last_index"] = new_index
    state["last_batch"] = batch
    state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(ROTATION_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        
    return batch

async def human_pause(min_sec=3.5, max_sec=6.0):
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

async def harvest_fresh_batch(batch_size=8, custom_accounts=None, deep_scroll_steps=12):
    all_handles, acc_map = load_benchmark_directory()
    accounts = custom_accounts or get_next_accounts_batch(batch_size)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Deep-Scroll & Adaptive-Floor Harvester on {len(accounts)} accounts...")
    
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if 'instagram.com' in t.get('url', '')]
    if not ig_targets:
        print("[!] Error: No Instagram tab found.")
        await cdp.close()
        return
        
    sid = await cdp.attach_page(ig_targets[0]['targetId'])
    os.makedirs("downloads/frames", exist_ok=True)
    results = []
    
    for idx, acc in enumerate(accounts, 1):
        meta = acc_map.get(acc.lower(), {})
        floor = get_adaptive_floor(acc, acc_map)
        cluster = meta.get("cluster", "دلنوشته و تکست")
        is_declamation = any(term in cluster for term in ["دکلمه", "نریشن", "صوتی", "پادکست"])
        
        print(f"\n({idx}/{len(accounts)}) [DEEP-HARVEST] @{acc}/reels/ | Floor: {floor:,} views | Cluster: {cluster}")
        await cdp.navigate(sid, f"https://www.instagram.com/{acc}/reels/")
        await human_pause(4.0, 5.5)
        
        # Idea 1: Deep scrolling (10 to 14 steps gradual human-like scroll)
        print(f"  -> Performing {deep_scroll_steps} deep-scroll steps...")
        for s in range(deep_scroll_steps):
            scroll_amount = random.randint(550, 950)
            await cdp.evaluate(sid, f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(1.6, 2.8))
        
        # Collect links with view badges
        script = """
        (() => {
            let links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
            let data = [];
            for (let a of links) {
                let href = a.href;
                let spans = Array.from(a.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean);
                data.push({url: href, badges: spans});
            }
            return data;
        })()
        """
        reels_data = await cdp.evaluate(sid, script)
        print(f"  Found {len(reels_data or [])} reel links on @{acc} (Depth: {deep_scroll_steps})")
        
        # Idea 2: Filter with Adaptive View Floor
        account_cands = 0
        for item in (reels_data or []):
            url = item["url"]
            badges = item["badges"]
            views_str = "Unknown"
            views_num = 0
            for b in badges:
                b_clean = b.replace(',', '').replace('،', '')
                if 'M' in b:
                    try:
                        views_num = int(float(b.replace('M', '')) * 1000000)
                        views_str = b
                    except: pass
                elif 'K' in b:
                    try:
                        views_num = int(float(b.replace('K', '')) * 1000)
                        views_str = b
                    except: pass
                    
            # Check against adaptive floor
            if views_num >= floor or 'M' in views_str:
                shortcode = url.strip('/').split('/')[-1]
                results.append({
                    "account": f"@{acc}",
                    "account_name": meta.get("name_fa", acc),
                    "cluster": cluster,
                    "is_declamation_candidate": is_declamation,
                    "url": url,
                    "shortcode": shortcode,
                    "views_str": views_str,
                    "views": views_num,
                    "matching_archetypes": meta.get("matching_archetypes", ["آرکتایپ ۱"])
                })
                account_cands += 1
                
        print(f"  [+] Extracted {account_cands} candidates meeting {floor:,} view floor from @{acc}")
        await human_pause(2.5, 4.0)
                
    # Save results incrementally
    out_file = "data/live_harvested_cands.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\n[DONE] Successfully harvested {len(results)} high-potential candidates across {len(accounts)} accounts!")
    await cdp.close()

if __name__ == "__main__":
    b_size = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    asyncio.run(harvest_fresh_batch(batch_size=b_size, deep_scroll_steps=depth))
