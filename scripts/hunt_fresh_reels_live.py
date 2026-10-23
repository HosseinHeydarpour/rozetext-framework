import asyncio
import sys, os, json, time, random, re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('scripts'))
from chrome_cdp import ChromeCDP
from anti_duplication import AntiDuplicationEngine
from harvest_fresh_batch import (
    load_benchmark_directory,
    get_adaptive_floor,
    get_next_accounts_batch,
    human_pause
)

async def hunt_pipeline(batch_size=8, deep_scroll_steps=12, max_reels_target=21):
    engine = AntiDuplicationEngine.get_instance()
    db_path = 'data/scripts-db.json'
    db_urls = set()
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                db = json.load(f)
            db_urls = {s.get('source_url') for s in db.get('scripts', []) if s.get('source_url')}
        except Exception as e:
            print(f"[!] Warning reading db: {e}")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing Single-Session Live Hunter...")
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("Error: No Instagram tab found! Please open Instagram in Chrome port 9222.")
        await cdp.close()
        return

    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Attached to Instagram session: {sid}")

    # Load benchmark accounts & mapping
    all_handles, acc_map = load_benchmark_directory()
    selected_accounts = get_next_accounts_batch(batch_size=batch_size)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Hunting batch of {len(selected_accounts)} benchmark accounts (from pool of {len(all_handles)}): {selected_accounts}")
    
    verified_batch = []
    start_time = time.time()
    last_report_time = time.time()
    
    for acc_idx, account in enumerate(selected_accounts, 1):
        if len(verified_batch) >= max_reels_target:
            break
            
        meta = acc_map.get(account.lower(), {})
        floor = get_adaptive_floor(account, acc_map)
        cluster = meta.get("cluster", "دلنوشته و تکست")
        is_declamation = any(term in cluster for term in ["دکلمه", "نریشن", "صوتی", "پادکست"])

        print(f"\n({acc_idx}/{len(selected_accounts)}) [{datetime.now().strftime('%H:%M:%S')}] Navigating to profile: @{account}/reels/ (Floor: {floor:,} views | {cluster})")
        await cdp.navigate(sid, f"https://www.instagram.com/{account}/reels/")
        await human_pause(3.5, 5.0)
        
        # Strategy 1: Deep scrolling (10 to 14 steps gradual human-like scroll)
        print(f"  -> Performing {deep_scroll_steps} deep-scroll steps to uncover viral archives...")
        for s in range(deep_scroll_steps):
            scroll_amount = random.randint(550, 950)
            await cdp.evaluate(sid, f"window.scrollBy(0, {scroll_amount})")
            await asyncio.sleep(random.uniform(1.6, 2.7))
            
        # Strategy 2: Collect reel links WITH view badges directly from grid
        grid_script = """
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
        reels_data = await cdp.evaluate(sid, grid_script) or []
        print(f"  -> Found {len(reels_data)} total reels in grid after {deep_scroll_steps} scrolls.")
        
        # Filter matching adaptive floor before navigating
        qualifying_reels = []
        for item in reels_data:
            url = item.get("url", "")
            if not url or url in db_urls:
                continue
            badges = item.get("badges", [])
            views_str = "0"
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
            
            if views_num >= floor or 'M' in views_str:
                qualifying_reels.append({
                    "url": url,
                    "views": views_num,
                    "views_str": views_str
                })

        print(f"  -> {len(qualifying_reels)} reels meet the adaptive floor of {floor:,} views.")

        for r_item in qualifying_reels:
            if len(verified_batch) >= max_reels_target:
                break
                
            r_url = r_item["url"]
            # Periodic 5-min report
            now = time.time()
            if now - last_report_time >= 300:
                last_report_time = now
                elapsed_min = int((now - start_time) / 60)
                print(f"\n>>> [5-MIN INTERVAL REPORT | {datetime.now().strftime('%H:%M:%S')}] Elapsed: {elapsed_min}m | Verified so far: {len(verified_batch)}/{max_reels_target} <<<")

            print(f"   [*] Inspecting qualifying reel: {r_url} ({r_item['views_str']} views)...")
            await cdp.navigate(sid, r_url)
            await human_pause(2.5, 4.0)
            
            inspect_script = """
            (() => {
                let video = document.querySelector('video');
                let h1 = document.querySelector('h1');
                let caption = h1 ? h1.innerText : '';
                let spans = Array.from(document.querySelectorAll('article span, main span'))
                    .map(s => s.innerText.trim())
                    .filter(t => t.length > 5);
                
                return {
                    hasVideo: !!video,
                    duration: video ? video.duration : 0,
                    caption: caption,
                    allSpans: spans.slice(0, 30)
                };
            })()
            """
            reel_info = await cdp.evaluate(sid, inspect_script) or {}
            shortcode = r_url.strip('/').split('/')[-1]
            
            cand_entry = {
                "account": f"@{account}",
                "account_name": meta.get("name_fa", account),
                "cluster": cluster,
                "is_declamation_candidate": is_declamation,
                "url": r_url,
                "shortcode": shortcode,
                "views": r_item["views"],
                "views_str": r_item["views_str"],
                "has_video": reel_info.get("hasVideo", False),
                "duration": reel_info.get("duration", 0),
                "caption": reel_info.get("caption", ""),
                "spans": reel_info.get("allSpans", []),
                "matching_archetypes": meta.get("matching_archetypes", ["آرکتایپ ۱"])
            }
            verified_batch.append(cand_entry)
            print(f"      [+] Added candidate {len(verified_batch)}/{max_reels_target}: shortcode={shortcode} (hasVideo={cand_entry['has_video']}, dur={cand_entry['duration']:.1f}s)")
            await human_pause(2.0, 3.5)

    # Save to live harvested candidates file
    out_file = "data/live_harvested_cands.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(verified_batch, f, ensure_ascii=False, indent=2)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Live Hunting completed! Total verified: {len(verified_batch)} (Saved to {out_file})")
    await cdp.close()

if __name__ == "__main__":
    batch_sz = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    asyncio.run(hunt_pipeline(batch_size=batch_sz, deep_scroll_steps=depth))
