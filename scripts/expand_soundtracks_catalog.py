import os
import sys
import json
import re
import csv
import glob
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_DLP = r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Scripts\yt-dlp.EXE"
FFMPEG_DIR = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin"
FFPROBE_EXE = os.path.join(FFMPEG_DIR, "ffprobe.exe")

# 1. Load scripts-db.json
with open(os.path.join(BASE_DIR, "data", "scripts-db.json"), "r", encoding="utf-8") as f:
    s_db = json.load(f)

persian_to_eng = {'۱': 1, '۲': 2, '۳': 3, '۴': 4, '۵': 5, '۶': 6, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6}

# Extract all reels from scripts-db
sc_catalog = {}
for s in s_db.get("scripts", []):
    u = (s.get("source_url") or "").strip()
    m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", u)
    if m:
        sc = m.group(1)
        arch = str(s.get("archetype_id") or s.get("archetype") or "")
        arch_num = 1
        for p, e in persian_to_eng.items():
            if p in arch:
                arch_num = e
                break
        t = s.get("title") or s.get("hook") or ""
        views = 0
        mv = re.search(r"(\d+(?:\.\d+)?)\s*(میلیون|هزار)", t)
        if mv:
            val = float(mv.group(1))
            views = int(val * 1_000_000) if "میلیون" in mv.group(2) else int(val * 1_000)
            
        sc_catalog[sc] = {
            "shortcode": sc,
            "url": u,
            "archetype": arch_num,
            "title": t,
            "views": views,
            "shares": 0,
            "viral_score": views
        }

# 2. Extract and correlate with Meta Business Suite CSVs
csv_files = glob.glob(r"D:\زر تکست\**\*.csv", recursive=True)
for cp in csv_files:
    try:
        with open(cp, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for r in reader:
                u = (r.get("Permalink") or "").strip()
                m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", u)
                if m:
                    sc = m.group(1)
                    vw = int(r.get("Views") or 0)
                    sh = int(r.get("Shares") or 0)
                    sv = int(r.get("Saves") or 0)
                    score = vw + (sh * 10) + (sv * 5)
                    desc = r.get("Description") or ""
                    
                    if sc in sc_catalog:
                        sc_catalog[sc]["views"] = max(sc_catalog[sc]["views"], vw)
                        sc_catalog[sc]["shares"] = max(sc_catalog[sc]["shares"], sh)
                        sc_catalog[sc]["viral_score"] = max(sc_catalog[sc]["viral_score"], score)
                    else:
                        # Archetype heuristic classifier from caption keywords
                        arch_guess = 1
                        if any(w in desc for w in ["خداحافظ", "رفت", "پایان", "دلتنگ", "تموم"]):
                            arch_guess = 2
                        elif any(w in desc for w in ["رفیق", "امن", "پناه", "دوست", "معرفت"]):
                            arch_guess = 3
                        elif any(w in desc for w in ["سکوت", "عصبی", "حد", "مرز", "قوی", "تلافی"]):
                            arch_guess = 4
                        elif any(w in desc for w in ["قضاوت", "اصالت", "عدالت", "خدا", "رفتار"]):
                            arch_guess = 5
                        elif any(w in desc for w in ["قهری", "چند روزه", "رها", "خودت"]):
                            arch_guess = 6
                            
                        first_line = desc.strip().split("\n")[0][:45] if desc else "ریلز RozeText"
                        sc_catalog[sc] = {
                            "shortcode": sc,
                            "url": u,
                            "archetype": arch_guess,
                            "title": first_line,
                            "views": vw,
                            "shares": sh,
                            "viral_score": score
                        }
    except Exception as e:
        print(f"Error reading CSV {cp}:", e)

print(f"Total classified reels available: {len(sc_catalog)}")

# Group by archetype
archetype_pools = {i: [] for i in range(1, 7)}
for sc, item in sc_catalog.items():
    archetype_pools[item["archetype"]].append(item)

# Sort each archetype pool by viral_score descending (Views + Shares weight)
for a in range(1, 7):
    archetype_pools[a].sort(key=lambda x: x["viral_score"], reverse=True)
    print(f"Archetype {a}: {len(archetype_pools[a])} reels in pool")

soundtracks_dir = os.path.join(BASE_DIR, "assets", "soundtracks")
os.makedirs(soundtracks_dir, exist_ok=True)

# Download and keep tracks for each archetype
# Target: up to 10-15 top viral tracks per archetype
for a in range(1, 7):
    a_dir = os.path.join(soundtracks_dir, f"archetype_{a}")
    os.makedirs(a_dir, exist_ok=True)
    
    # Check existing files
    existing_files = [f for f in os.listdir(a_dir) if f.endswith(".mp3")]
    existing_scs = set()
    for ef in existing_files:
        m = re.search(r"track_\d+_([A-Za-z0-9_-]+)\.mp3", ef)
        if m:
            existing_scs.add(m.group(1))
            
    print(f"\n--- Archetype {a} (Current: {len(existing_files)} tracks) ---")
    
    pool = archetype_pools[a]
    for item in pool[:15]:
        sc = item["shortcode"]
        if sc in existing_scs:
            continue
            
        rank = len(existing_files) + 1
        target_fn = f"track_{rank}_{sc}.mp3"
        target_path = os.path.join(a_dir, target_fn)
        
        print(f"Downloading Arch {a} Rank {rank} ({sc}) [Views: {item['views']:,}]...")
        cmd = [
            YT_DLP,
            "--no-warnings",
            "-x", "--audio-format", "mp3",
            "--ffmpeg-location", FFMPEG_DIR,
            "-o", os.path.join(a_dir, f"track_{rank}_{sc}.%(ext)s"),
            item["url"]
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and os.path.exists(target_path):
                print(f"   Saved: {target_fn} ({os.path.getsize(target_path)} bytes)")
                existing_files.append(target_fn)
                existing_scs.add(sc)
            else:
                pass
        except Exception as ex:
            print(f"   Timeout/Error on {sc}:", ex)

# Rebuild catalog.json with viral ranking
catalog = {"archetypes": {}}
for a in range(1, 7):
    a_dir = os.path.join(soundtracks_dir, f"archetype_{a}")
    catalog["archetypes"][str(a)] = []
    if not os.path.exists(a_dir):
        continue
        
    files = sorted([f for f in os.listdir(a_dir) if f.endswith(".mp3")])
    temp_list = []
    for f in files:
        f_path = os.path.join(a_dir, f)
        m = re.search(r"track_\d+_([A-Za-z0-9_-]+)\.mp3", f)
        sc = m.group(1) if m else f
        meta = sc_catalog.get(sc, {})
        
        # probe duration
        dur = 7.0
        try:
            cmd = [FFPROBE_EXE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f_path]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.stdout.strip():
                dur = round(float(r.stdout.strip()), 2)
        except Exception:
            pass
            
        temp_list.append({
            "filename": f,
            "relative_path": f"assets/soundtracks/archetype_{a}/{f}".replace("\\", "/"),
            "shortcode": sc,
            "title": meta.get("title") or f,
            "views": meta.get("views", 0),
            "shares": meta.get("shares", 0),
            "viral_score": meta.get("viral_score", 0),
            "duration_seconds": dur,
            "url": meta.get("url", ""),
            "filesize": os.path.getsize(f_path)
        })
        
    # Sort strictly by viral_score descending so top viral track is always first!
    temp_list.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
    catalog["archetypes"][str(a)] = temp_list

catalog_path = os.path.join(soundtracks_dir, "catalog.json")
with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("\nCatalog updated successfully with Viral Ranking!")
for a in range(1, 7):
    print(f"Archetype {a}: {len(catalog['archetypes'][str(a)])} tracks available")
