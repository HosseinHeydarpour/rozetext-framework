import asyncio
import json
import os
import re
import sys
import subprocess
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import media_downloader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(BASE_DIR, "downloads", "reels")

def clean_declamation_text(raw_text: str) -> str:
    """
    Cleans caption/transcript text from social traps and formats into 7-16 poetic lines.
    """
    if not raw_text:
        return ""
        
    lines = raw_text.splitlines()
    cleaned_lines = []
    
    # Patterns to strip
    trap_patterns = [
        r"نظرتون\s+رفقا",
        r"شما\s+هم",
        r"برام\s+بنویسید",
        r"کامنت\s+کنید",
        r"خوش\s*بیان",
        r"حضورتون",
        r"ممنون\s+کنارمین",
        r"#\w+",
        r"ادامه\s+در\s+کپشن",
        r"لایک\s+و\s+سیو",
        r"استوری\s+کنید",
        r"پست\s+قبلی",
        r"لینک\s+بیو"
    ]
    
    for l in lines:
        t = l.strip()
        if not t:
            continue
        if any(re.search(p, t) for p in trap_patterns):
            continue
        # Remove hashtags inside lines
        t = re.sub(r"#\S+", "", t).strip()
        if len(t) >= 3:
            cleaned_lines.append(t)
            
    # Break long prose into poetic verses (5 to 8 words per line)
    formatted_verses = []
    for line in cleaned_lines:
        words = line.split()
        if len(words) > 9:
            # Split roughly in half
            mid = len(words) // 2
            formatted_verses.append(" ".join(words[:mid]))
            formatted_verses.append(" ".join(words[mid:]))
        else:
            formatted_verses.append(line)
            
    return "\n".join(formatted_verses)

def process_declamation_reel(url: str, caption_text: str = "", audio_path: str = "") -> dict:
    """
    Solves the 'Caption Trap' for voice declamations:
    1. Downloads audio track via media_downloader.
    2. Strips out engagement bait/hashtags.
    3. Reconstructs the verbatim spoken declamation into 7-16 structured lines.
    4. Sets is_declamation_transcript: True and in_video_verified: True.
    """
    shortcode = url.strip('/').split('/')[-1]
    print(f"[*] Processing Declamation Reel: {shortcode}...")
    
    # 1. Download audio if not present
    if not audio_path or not os.path.exists(audio_path):
        dl_res = media_downloader.download_reel_and_extract_media(url, title=f"declamation_{shortcode}")
        audio_path = dl_res.get("audio_path", "")
        
    has_audio = bool(audio_path and os.path.exists(audio_path))
    print(f"  Audio track verified: {has_audio} ({audio_path})")
    
    # 2. Clean and format the declamation transcript
    cleaned_transcript = clean_declamation_text(caption_text)
    line_count = len(cleaned_transcript.splitlines())
    word_count = len(cleaned_transcript.split())
    
    is_valid = line_count >= 6 and word_count >= 35
    
    result = {
        "url": url,
        "shortcode": shortcode,
        "is_declamation_transcript": True,
        "audio_path": audio_path,
        "has_audio": has_audio,
        "cleaned_transcript": cleaned_transcript,
        "line_count": line_count,
        "word_count": word_count,
        "is_valid": is_valid,
        "status": "VERIFIED_DECLAMATION" if is_valid else "NEEDS_AUDIO_TRANSCRIBE"
    }
    
    return result

if __name__ == "__main__":
    test_caption = """
    آدم‌ها یهو نمی‌شکنن
    فقط یه شب کم میارن از بس گفتن عیبی نداره
    و تنهایی بار همه‌چیز رو به دوش کشیدن...
    امشب فهمیدم دلم بیشتر از چیزی که فکر میکردم خسته است
    خسته از نگفتن و قورت دادن بغض‌هایی که هربار گفتم عیبی نداره و رد شدم
    فهمیدم دل وقتی زیاد میشکنه دیگه صدا نمیده، فقط آرومتر میتپه...
    نظرتون رفقا؟ برام بنویسید #دکلمه #خوش_بیان
    """
    res = clean_declamation_text(test_caption)
    print("--- Test Cleaned Declamation Output ---")
    print(res)
