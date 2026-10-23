import asyncio
import json
import os
import random
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from chrome_cdp import ChromeCDP

BENCHMARK_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_accounts.json")
OUTPUT_AUDIT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "benchmark_audit_results.json")

async def human_delay(min_sec=3.5, max_sec=6.0):
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)

async def verify_and_expand(batch_size=15, start_index=0):
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    accounts = data.get("accounts", [])
    total = len(accounts)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loaded {total} benchmark accounts.")
    
    cdp = ChromeCDP()
    await cdp.connect()
    targets = await cdp.list_targets()
    ig_targets = [t for t in targets if "instagram.com" in t.get("url", "")]
    if not ig_targets:
        print("[!] Error: No Instagram tab found in Chrome.")
        await cdp.close()
        return

    # Use first available IG target or open new
    sid = await cdp.attach_page(ig_targets[0]["targetId"])
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Attached to Chrome CDP session: {sid}")

    # Verify session user
    user_check_script = """
    (() => {
        let ds = document.cookie.match(/ds_user_id=([^;]+)/);
        let img = document.querySelector('img[alt*="profile picture"]');
        return {
            ds_user_id: ds ? ds[1] : null,
            imgAlt: img ? img.alt : null
        };
    })()
    """
    user_info = await cdp.evaluate(sid, user_check_script)
    print(f"[*] Verified Active User: {user_info.get('imgAlt')} (ID: {user_info.get('ds_user_id')})")

    audit_results = {}
    if os.path.exists(OUTPUT_AUDIT_PATH):
        try:
            with open(OUTPUT_AUDIT_PATH, "r", encoding="utf-8") as f:
                audit_results = json.load(f)
        except Exception:
            audit_results = {}

    discovered_candidates = set(audit_results.get("_discovered_candidates", []))
    verified_accounts = audit_results.get("verified_accounts", {})

    target_batch = accounts[start_index : start_index + batch_size]
    print(f"[*] Processing batch: indices {start_index} to {start_index + len(target_batch)} of {total} accounts...")

    for idx, acc in enumerate(target_batch, start=start_index + 1):
        handle = acc.get("handle", "").replace("@", "").strip()
        url = f"https://www.instagram.com/{handle}/"
        print(f"\n({idx}/{total}) Checking @{handle} -> {url}")
        
        try:
            await cdp.navigate(sid, url)
            await human_delay(3.0, 4.5)

            inspect_page_script = """
            (() => {
                let title = document.title;
                let isUnavailable = document.body ? (
                    document.body.innerText.includes("Sorry, this page isn't available") ||
                    document.body.innerText.includes("صفحه مورد نظر در دسترس نیست") ||
                    title.includes("Unavailable")
                ) : false;

                // Extract follower count and bio
                let header = document.querySelector('header');
                let headerText = header ? header.innerText : '';
                
                // Look for follower numbers in header
                let followers = null;
                let spans = Array.from(document.querySelectorAll('header span, header a'));
                for (let s of spans) {
                    let t = s.innerText.trim();
                    if (t.includes('followers') || t.includes('دنبال‌کننده') || t.includes('فالوور')) {
                        followers = t;
                        break;
                    }
                }

                const systemPaths = ['explore', 'reels', 'direct', 'stories', 'accounts', 'legal', 'popular', 'about', 'privacy', 'terms', 'language', 'help', 'press', 'api', 'jobs', 'locations', 'meta_verified'];
                let suggested = [];
                let suggestionLinks = Array.from(document.querySelectorAll('a[href^="/"]'));
                for (let a of suggestionLinks) {
                    let h = a.getAttribute('href') || '';
                    let match = h.match(/^\/([a-zA-Z0-9_\.]+)\/$/);
                    if (match) {
                        let candidate = match[1].toLowerCase();
                        if (!systemPaths.includes(candidate) && candidate !== 'hosseinheydarpour' && candidate.length > 2) {
                            suggested.push(candidate);
                        }
                    }
                }

                return {
                    title: title,
                    isUnavailable: isUnavailable,
                    followersSnippet: followers,
                    headerSnippet: headerText.slice(0, 300),
                    suggested: Array.from(new Set(suggested)).slice(0, 10)
                };
            })()
            """
            res = await cdp.evaluate(sid, inspect_page_script)
            is_valid = not res.get("isUnavailable")
            status = "VALID_ACTIVE" if is_valid else "UNAVAILABLE_OR_CHANGED"
            
            print(f"    Status: {status} | Title: {res.get('title', '')[:40]}")
            if res.get("followersSnippet"):
                print(f"    Followers: {res.get('followersSnippet')}")
            
            # Add discovered suggested accounts
            for s in res.get("suggested", []):
                if s.lower() != handle.lower():
                    discovered_candidates.add(s)

            verified_accounts[handle] = {
                "handle": f"@{handle}",
                "name_fa": acc.get("name_fa"),
                "cluster": acc.get("cluster"),
                "status": status,
                "title": res.get("title"),
                "is_active": is_valid,
                "followers_detected": res.get("followersSnippet"),
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Human-like micro scroll
            await cdp.evaluate(sid, "window.scrollBy(0, 400);")
            await human_delay(1.5, 2.5)

        except Exception as e:
            print(f"    [!] Error checking @{handle}: {e}")
            verified_accounts[handle] = {
                "handle": f"@{handle}",
                "status": "ERROR",
                "error": str(e),
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        # Save progress after each account
        audit_results["verified_accounts"] = verified_accounts
        audit_results["_discovered_candidates"] = list(discovered_candidates)
        with open(OUTPUT_AUDIT_PATH, "w", encoding="utf-8") as f:
            json.dump(audit_results, f, ensure_ascii=False, indent=2)

    await cdp.close()
    print(f"\n[+] Batch finished! Total verified so far: {len(verified_accounts)} / Discovered new candidates: {len(discovered_candidates)}")

if __name__ == "__main__":
    b_size = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    s_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    asyncio.run(verify_and_expand(batch_size=b_size, start_index=s_idx))
