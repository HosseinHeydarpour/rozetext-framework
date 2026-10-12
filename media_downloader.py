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
