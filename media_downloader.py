import os
import re
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads", "reels")

def open_in_explorer(target_path: str) -> bool:
    """Safely opens Windows File Explorer selecting the target file or directory."""
    try:
        if not target_path:
            return False
        # Normalize slashes for Windows
        norm_p = os.path.normpath(os.path.abspath(target_path.replace("/", "\\")))
        print(f"[open_in_explorer] Normalized path: {norm_p}")

        if os.path.isfile(norm_p):
            cmd = f'explorer.exe /select,"{norm_p}"'
            try:
                subprocess.Popen(cmd, shell=True)
                return True
            except Exception as e:
                folder = os.path.dirname(norm_p)
                os.startfile(folder)
                return True
        elif os.path.isdir(norm_p):
            os.startfile(norm_p)
            return True
        else:
            ext = os.path.splitext(norm_p)[1]
            if not ext:
                os.makedirs(norm_p, exist_ok=True)
                os.startfile(norm_p)
                return True
            parent = os.path.dirname(norm_p)
            if os.path.isdir(parent):
                os.startfile(parent)
                return True
        return False
    except Exception as e:
        print("[open_in_explorer] Error opening explorer:", e)
        return False

def download_reel_and_extract_media(
    url: str,
    title: str = "",
    scheduled_date: str = "",
    scheduled_slot: int = None,
    custom_directory: str = ""
) -> dict:
    """
    Downloads Instagram Reel video (.mp4) via yt-dlp,
    extracts high-quality audio track (.mp3) via ffmpeg,
    names files according to date and slot number,
    saves into custom day directory,
    and opens Windows File Explorer selecting the audio file.
    """
    if not url or not url.strip():
        return {"ok": False, "error": "آدرس اینترنتی ریلز (URL) نامعتبر یا خالی است."}

    url = url.strip()

    # Extract shortcode
    m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", url)
    if m:
        shortcode = m.group(1)
    else:
        cleaned_title = re.sub(r"[^\w\u0600-\u06FF]+", "_", title).strip("_")[:30]
        shortcode = cleaned_title or f"reel_{int(os.path.getmtime(BASE_DIR))}"

    # Determine destination folder
    if custom_directory and custom_directory.strip():
        dest_folder = os.path.normpath(os.path.abspath(custom_directory.strip().replace("/", "\\")))
    elif scheduled_date and scheduled_date.strip():
        dest_folder = os.path.normpath(os.path.join(DOWNLOADS_DIR, scheduled_date.strip()))
    else:
        dest_folder = os.path.normpath(os.path.join(DOWNLOADS_DIR, shortcode))

    os.makedirs(dest_folder, exist_ok=True)

    # Determine file naming according to date and slot number
    if scheduled_date and scheduled_slot:
        try:
            slot_num = int(scheduled_slot)
            prefix = f"{scheduled_date}_Slot-{slot_num:02d}_{shortcode}"
        except Exception:
            prefix = f"{scheduled_date}_{shortcode}"
    elif scheduled_slot:
        try:
            slot_num = int(scheduled_slot)
            prefix = f"Slot-{slot_num:02d}_{shortcode}"
        except Exception:
            prefix = shortcode
    else:
        prefix = shortcode

    video_filename = f"{prefix}_video.mp4"
    audio_filename = f"{prefix}_audio.mp3"

    video_path = os.path.normpath(os.path.join(dest_folder, video_filename))
    audio_path = os.path.normpath(os.path.join(dest_folder, audio_filename))

    # 1. Download video with yt-dlp if not present or empty
    need_download = not os.path.exists(video_path) or os.path.getsize(video_path) < 1000

    if need_download:
        # Check if already downloaded anywhere in cache
        cached_candidates = [
            os.path.join(BASE_DIR, f"reel_{shortcode}.mp4"),
            os.path.join(DOWNLOADS_DIR, shortcode, f"{shortcode}_video.mp4"),
        ]
        found_cache = False
        for c in cached_candidates:
            if os.path.exists(c) and os.path.getsize(c) > 1000:
                shutil.copy2(c, video_path)
                found_cache = True
                break

        if not found_cache:
            yt_cmd = [
                sys.executable, "-m", "yt_dlp",
                "--no-warnings",
                "--no-check-certificates",
                "-f", "bestvideo+bestaudio/best",
                "--merge-output-format", "mp4",
                "-o", video_path,
                url
            ]
            res_yt = subprocess.run(yt_cmd, capture_output=True, text=True, timeout=90)
            if res_yt.returncode != 0:
                err_msg = res_yt.stderr or res_yt.stdout or "خطا در دانلود ریلز با yt-dlp"
                return {"ok": False, "error": f"خطا در دانلود ویدیو: {err_msg[:250]}"}

    if not os.path.exists(video_path) or os.path.getsize(video_path) < 1000:
        return {"ok": False, "error": "فایل ویدیوی ریلز پس از دانلود یافت نشد."}

    # 2. Extract MP3 audio via ffmpeg if not present or empty
    need_audio = not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000
    if need_audio:
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            audio_path
        ]
        res_ff = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=45)
        if res_ff.returncode != 0 or not os.path.exists(audio_path):
            err_msg = res_ff.stderr or "خطا در استخراج صدای mp3 با ffmpeg"
            return {"ok": False, "error": f"خطا در جداسازی صدا: {err_msg[:250]}"}

    # 2.5 Extract Keyframe PNG at 2.0s for side-by-side post maker reference
    frames_global_dir = os.path.join(BASE_DIR, "downloads", "frames")
    os.makedirs(frames_global_dir, exist_ok=True)
    frame_global_path = os.path.normpath(os.path.join(frames_global_dir, f"{shortcode}_frame.png"))
    frame_local_path = os.path.normpath(os.path.join(dest_folder, f"{prefix}_frame.png"))
    
    if not os.path.exists(frame_global_path) or os.path.getsize(frame_global_path) < 1000:
        ff_frame_cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:02",
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            frame_global_path
        ]
        subprocess.run(ff_frame_cmd, capture_output=True, timeout=30)
        if os.path.exists(frame_global_path):
            try:
                shutil.copy2(frame_global_path, frame_local_path)
            except Exception:
                pass

    # 3. Open Windows Explorer highlighting the audio file
    open_in_explorer(audio_path)

    # Relative web URL if inside web directory
    web_audio_url = ""
    try:
        rel_audio = os.path.relpath(audio_path, BASE_DIR).replace("\\", "/")
        if not rel_audio.startswith(".."):
            web_audio_url = f"/{rel_audio}"
    except Exception:
        web_audio_url = ""

    return {
        "ok": True,
        "shortcode": shortcode,
        "video_path": video_path,
        "audio_path": audio_path,
        "folder_path": dest_folder,
        "audio_filename": audio_filename,
        "video_filename": video_filename,
        "web_audio_url": web_audio_url,
        "scheduled_slot": scheduled_slot,
        "scheduled_date": scheduled_date,
        "message": f"فایل صوتی {audio_filename} با موفقیت در پوشه {dest_folder} ذخیره شد و در File Explorer باز شد!"
    }


def extract_audio_from_local_video(
    video_path: str,
    title: str = "",
    scheduled_date: str = "",
    scheduled_slot: int = None,
    custom_directory: str = "",
    open_explorer: bool = False
) -> dict:
    """
    Extracts high-quality MP3 audio track from a local video file using FFmpeg,
    names the audio file according to date and slot number,
    saves into custom day directory or downloads/reels/{date},
    and returns metadata including relative path for web and Post Maker video generation.
    """
    if not video_path or not os.path.isfile(video_path):
        return {"ok": False, "error": f"فایل ویدیوی ریلز در مسیر مشخص‌شده یافت نشد: {video_path}"}

    # Extract base name without extension
    raw_stem = os.path.splitext(os.path.basename(video_path))[0]
    cleaned_stem = re.sub(r"[^\w\u0600-\u06FF]+", "_", title or raw_stem).strip("_")[:35]
    shortcode = cleaned_stem or f"reel_{int(os.path.getmtime(video_path))}"

    # Determine destination folder
    if custom_directory and custom_directory.strip():
        dest_folder = os.path.normpath(os.path.abspath(custom_directory.strip().replace("/", "\\")))
    elif scheduled_date and scheduled_date.strip():
        dest_folder = os.path.normpath(os.path.join(DOWNLOADS_DIR, scheduled_date.strip()))
    else:
        dest_folder = os.path.normpath(os.path.join(DOWNLOADS_DIR, "custom"))

    os.makedirs(dest_folder, exist_ok=True)

    # Determine file naming
    if scheduled_date and scheduled_slot:
        try:
            slot_num = int(scheduled_slot)
            prefix = f"{scheduled_date}_Slot-{slot_num:02d}_{shortcode}"
        except Exception:
            prefix = f"{scheduled_date}_{shortcode}"
    elif scheduled_slot:
        try:
            slot_num = int(scheduled_slot)
            prefix = f"Slot-{slot_num:02d}_{shortcode}"
        except Exception:
            prefix = shortcode
    else:
        prefix = shortcode

    audio_filename = f"{prefix}_audio.mp3"
    audio_path = os.path.normpath(os.path.join(dest_folder, audio_filename))

    # Extract MP3 audio via ffmpeg (high-quality 320k stereo)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-c:a", "libmp3lame",
        "-b:a", "320k",
        "-ac", "2",
        "-ar", "44100",
        audio_path
    ]
    res_ff = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
    if res_ff.returncode != 0 or not os.path.exists(audio_path) or os.path.getsize(audio_path) < 100:
        # Fallback command without strict ac/ar in case video stream has unique sample rate
        fallback_cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-vn",
            "-c:a", "libmp3lame",
            "-q:a", "2",
            audio_path
        ]
        res_ff2 = subprocess.run(fallback_cmd, capture_output=True, text=True, timeout=60)
        if res_ff2.returncode != 0 or not os.path.exists(audio_path):
            err_msg = res_ff.stderr or res_ff2.stderr or "خطا در جداسازی صدای ویدیو با FFmpeg (احتمالاً فایل فاقد ترک صوتی است)"
            return {"ok": False, "error": f"خطا در جداسازی صدا: {err_msg[:250]}"}

    # Extract Keyframe PNG at 2.0s for side-by-side post maker reference
    frame_filename = f"{prefix}_frame.png"
    frame_local_path = os.path.normpath(os.path.join(dest_folder, frame_filename))
    try:
        ff_frame_cmd = [
            "ffmpeg", "-y",
            "-ss", "00:00:02",
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            frame_local_path
        ]
        subprocess.run(ff_frame_cmd, capture_output=True, timeout=20)
    except Exception:
        pass

    if open_explorer:
        open_in_explorer(audio_path)

    # Relative web URL if inside web directory
    web_audio_url = ""
    rel_audio = os.path.normpath(audio_path)
    try:
        rel_p = os.path.relpath(audio_path, BASE_DIR).replace("\\", "/")
        if not rel_p.startswith(".."):
            rel_audio = rel_p
            web_audio_url = f"/{rel_p}"
        else:
            import urllib.parse
            web_audio_url = f"/api/media/file-stream?path={urllib.parse.quote(audio_path)}"
    except Exception:
        web_audio_url = ""

    # Duration calculation
    try:
        scripts_dir = os.path.join(BASE_DIR, "scripts")
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        import post_maker
        dur = post_maker.get_audio_duration(audio_path)
    except Exception:
        dur = 7.0

    track_obj = {
        "filename": audio_filename,
        "relative_path": rel_audio,
        "shortcode": shortcode,
        "title": f"🎬 [صدای استخراج‌شده ریلز] {raw_stem[:28]}",
        "duration_seconds": dur,
        "filesize": os.path.getsize(audio_path),
        "is_source_track": True,
        "is_extracted_from_reel": True
    }

    return {
        "ok": True,
        "shortcode": shortcode,
        "video_path": video_path,
        "audio_path": audio_path,
        "folder_path": dest_folder,
        "audio_filename": audio_filename,
        "frame_path": frame_local_path if os.path.exists(frame_local_path) else "",
        "web_audio_url": web_audio_url,
        "duration_seconds": dur,
        "scheduled_slot": scheduled_slot,
        "scheduled_date": scheduled_date,
        "track": track_obj,
        "message": f"صدای ریلز با موفقیت استخراج و با نام {audio_filename} ذخیره شد."
    }


def list_system_downloaded_reels(date_str: str = "", custom_directory: str = "") -> list:
    """
    Finds recently downloaded reels/videos on the local system:
    1. In the day's custom directory or downloads/reels/{date}
    2. In all downloads/reels subdirectories
    3. In Windows ~/Downloads folder
    """
    found = []
    seen_paths = set()

    def add_video(p, loc_label):
        norm = os.path.normpath(os.path.abspath(p))
        if norm in seen_paths or not os.path.isfile(norm):
            return
        try:
            sz = os.path.getsize(norm)
            if sz < 10000:  # ignore empty or corrupt files (<10KB)
                return
            mtime = os.path.getmtime(norm)
            from datetime import datetime
            dt_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            seen_paths.add(norm)
            rel_p = ""
            try:
                rel = os.path.relpath(norm, BASE_DIR).replace("\\", "/")
                if not rel.startswith(".."):
                    rel_p = rel
            except Exception:
                rel_p = ""
            found.append({
                "path": norm,
                "relative_path": rel_p,
                "filename": os.path.basename(norm),
                "size_mb": round(sz / (1024 * 1024), 2),
                "modified": dt_str,
                "mtime": mtime,
                "location": loc_label
            })
        except Exception:
            pass

    # 1. Custom directory or today's reels folder
    if custom_directory and os.path.isdir(custom_directory):
        import glob
        for f in glob.glob(os.path.join(custom_directory, "*.mp4")) + glob.glob(os.path.join(custom_directory, "*.mov")):
            add_video(f, "پوشه اختصاصی روز")
    if date_str:
        day_dir = os.path.join(DOWNLOADS_DIR, date_str)
        if os.path.isdir(day_dir):
            import glob
            for f in glob.glob(os.path.join(day_dir, "*.mp4")):
                add_video(f, f"پوشه روز {date_str}")

    # 2. downloads/reels cache
    if os.path.isdir(DOWNLOADS_DIR):
        import glob
        for f in glob.glob(os.path.join(DOWNLOADS_DIR, "**", "*.mp4"), recursive=True):
            add_video(f, "پوشه ریلزهای پروژه")

    # 3. User's Windows Downloads folder
    user_dl = os.path.expanduser("~/Downloads")
    if os.path.isdir(user_dl):
        import glob
        dl_mp4s = glob.glob(os.path.join(user_dl, "*.mp4")) + glob.glob(os.path.join(user_dl, "*.mov"))
        dl_mp4s.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for f in dl_mp4s[:10]:
            add_video(f, "پوشه دانلودهای ویندوز (Downloads)")

    # Sort all found by mtime descending
    found.sort(key=lambda x: x["mtime"], reverse=True)
    return found[:25]

