import os
import sys
import json
import subprocess
import re

ffprobe = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe"

with open("data/scripts-db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

scripts = db.get("scripts", [])
shortcode_to_meta = {}
for s in scripts:
    url = (s.get("source_url") or "").strip()
    m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    if m:
        sc = m.group(1)
        shortcode_to_meta[sc] = {
            "title": s.get("title") or "",
            "hook": s.get("hook") or "",
            "archetype": s.get("archetype") or s.get("archetype_id") or "",
            "views": s.get("source_views") or s.get("views_raw") or 0,
            "url": url
        }

catalog = {"archetypes": {}}
base = "assets/soundtracks"

for a in range(1, 7):
    a_dir = os.path.join(base, f"archetype_{a}")
    catalog["archetypes"][str(a)] = []
    if not os.path.exists(a_dir):
        continue
    files = sorted([f for f in os.listdir(a_dir) if f.endswith(".mp3")])
    for f in files:
        f_path = os.path.join(a_dir, f)
        cmd = [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        dur = float(res.stdout.strip()) if res.stdout.strip() else 0.0
        
        m = re.search(r"track_\d+_([A-Za-z0-9_-]+)\.mp3", f)
        sc = m.group(1) if m else f
        meta = shortcode_to_meta.get(sc, {})
        catalog["archetypes"][str(a)].append({
            "filename": f,
            "relative_path": f"assets/soundtracks/archetype_{a}/{f}".replace("\\", "/"),
            "shortcode": sc,
            "title": meta.get("title") or f,
            "duration_seconds": round(dur, 2),
            "url": meta.get("url", ""),
            "filesize": os.path.getsize(f_path)
        })

with open("assets/soundtracks/catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("Catalog created successfully!")
for a in range(1, 7):
    tracks = catalog["archetypes"][str(a)]
    print(f"Archetype {a}: {len(tracks)} tracks")
    for t in tracks:
        print(f"    {t['filename']} ({t['duration_seconds']}s) - {t['title'][:35]}")
