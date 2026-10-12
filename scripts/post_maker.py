import os
import sys
import json
import re
import base64
import subprocess
import shutil
import tempfile
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "scripts-db.json")
CLEAN_PLATES_DIR = os.path.join(BASE_DIR, "assets", "clean_plates")

# Preload base64 images for 100% reliable local rendering
PLATES_BASE64 = {}
for name in ["dark_cover.png", "dark_text.png", "light_cover.png", "light_text.png"]:
    p = os.path.join(CLEAN_PLATES_DIR, name)
    if os.path.exists(p):
        with open(p, "rb") as f:
            PLATES_BASE64[name] = base64.b64encode(f.read()).decode("ascii")

# Preload base64 fonts for 100% guaranteed headless Chrome rendering (IRLotus Bold, Regular, IRTitr)
FONTS_BASE64 = {}
font_files = {
    "IRLotus": r"C:\Windows\Fonts\IRLotus.ttf",
    "IRLotusBold": r"C:\Windows\Fonts\IRLotusBold.ttf",
    "IRTitr": r"C:\Windows\Fonts\IRTitr.ttf",
}
for fname, fpath in font_files.items():
    if os.path.exists(fpath):
        try:
            with open(fpath, "rb") as f:
                FONTS_BASE64[fname] = base64.b64encode(f.read()).decode("ascii")
        except Exception:
            pass

FFMPEG_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"
FFPROBE_EXE = r"C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe"
SOUNDTRACKS_CATALOG_PATH = os.path.join(BASE_DIR, "assets", "soundtracks", "catalog.json")

def get_soundtracks_catalog():
    if os.path.exists(SOUNDTRACKS_CATALOG_PATH):
        try:
            with open(SOUNDTRACKS_CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"archetypes": {}}

def get_audio_duration(audio_path: str) -> float:
    if not os.path.exists(audio_path) or not os.path.exists(FFPROBE_EXE):
        return 7.0
    try:
        cmd = [FFPROBE_EXE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        dur = float(res.stdout.strip())
        return dur if dur > 1.0 else 7.0
    except Exception:
        return 7.0

def generate_post_video(text_png: str, audio_path: str, output_mp4: str) -> bool:
    """
    Generates 1080x1920 MP4 reel video from text post + audio track (NO cover inside the video).
    The cover is uploaded separately in Instagram.
    Matches user's exact Filmora export profile:
    - Quality: Higher
    - Resolution: 1080x1920 Custom
    - Frame Rate: 30 fps
    - Encoder: H.264 (High Profile, Level 4.1)
    - Bitrate Mode: VBR (20,000 kbps target, 25,000 kbps max)
    - Color Space: SDR - Rec.709 (bt709)
    - Audio: AAC, Stereo, 44100 Hz, 320 kbps
    - Moov Atom: +faststart for instant playback on all Windows players & Instagram
    """
    if not os.path.exists(FFMPEG_EXE) or not os.path.exists(text_png):
        return False
        
    dur = get_audio_duration(audio_path) if audio_path and os.path.exists(audio_path) else 7.0
    
    cmd = [
        FFMPEG_EXE, "-y",
        "-loop", "1",
        "-r", "30",
        "-i", text_png,
    ]
    
    if audio_path and os.path.exists(audio_path):
        cmd.extend([
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.1",
            "-pix_fmt", "yuv420p",
            "-b:v", "20000k",
            "-maxrate", "25000k",
            "-bufsize", "40000k",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
            "-color_range", "tv",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "44100",
            "-ac", "2",
            "-movflags", "+faststart",
            "-shortest",
            output_mp4
        ])
    else:
        # Video only without audio
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-profile:v", "high",
            "-level", "4.1",
            "-pix_fmt", "yuv420p",
            "-b:v", "20000k",
            "-maxrate", "25000k",
            "-bufsize", "40000k",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-colorspace", "bt709",
            "-color_range", "tv",
            "-movflags", "+faststart",
            "-t", str(dur),
            output_mp4
        ])
        
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        return res.returncode == 0 and os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1000
    except Exception as e:
        print(f"Error generating video {output_mp4}:", e)
        return False


def get_browser_executable():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    for b in ["chrome", "msedge"]:
        which = shutil.which(b)
        if which:
            return which
    return None

def get_slot_theme(slot: int) -> str:
    # 1, 2, 6: light | 3, 4, 5: dark
    return "light" if int(slot) in [1, 2, 6] else "dark"

def strip_emojis_and_replace_with_dots(text: str) -> str:
    """Removes all emojis and replaces them strictly with '...'. Avoids redundant dots."""
    if not text:
        return ""
    emoji_pattern = re.compile(
        r"[\U00010000-\U0010ffff]|[\u2600-\u27bf]|[\u2300-\u23ff]|[\u2b50-\u2b55]|[\ufe0f]",
        flags=re.UNICODE
    )
    # Replace emojis with ...
    replaced = emoji_pattern.sub("...", text)
    # Any sequence of dots (2 or more) strictly becomes '...'
    replaced = re.sub(r"\.{2,}", "...", replaced)
    # Clean up space before dots
    replaced = re.sub(r"\s+\.\.\.", "...", replaced)
    return replaced.strip()

def clean_hook_text(raw_hook: str, title: str, content: str) -> str:
    """Generates a high-impact 6-8 word hook based on RozeText persona DNA with emojis stripped."""
    candidates = []
    
    # Clean title
    if title:
        c_title = re.sub(r'\(.*?\)', '', title).strip()
        c_title = strip_emojis_and_replace_with_dots(c_title)
        c_title = c_title.rstrip('.،!؟: ')
        w_title = c_title.split()
        if 4 <= len(w_title) <= 9:
            candidates.append(" ".join(w_title[:8]))

    # Raw hook
    if raw_hook:
        c_hook = re.sub(r'\(.*?\)', '', raw_hook).strip()
        c_hook = strip_emojis_and_replace_with_dots(c_hook)
        c_hook = c_hook.rstrip('.،!؟: ')
        w_hook = c_hook.split()
        if 4 <= len(w_hook) <= 8:
            candidates.append(" ".join(w_hook))
        elif len(w_hook) < 4 and content:
            c_lines = [l.strip() for l in content.split('\n') if l.strip()]
            if len(c_lines) >= 2:
                comb = f"{c_hook} {c_lines[1]}"
                comb = re.sub(r'\(.*?\)', '', comb).strip()
                comb = strip_emojis_and_replace_with_dots(comb).rstrip('.،!؟: ')
                w_comb = comb.split()
                if 5 <= len(w_comb) <= 10:
                    candidates.append(" ".join(w_comb[:8]))
                    
    # Content first line
    if not candidates and content:
        c_lines = [l.strip() for l in content.split('\n') if l.strip()]
        if c_lines:
            c_first = strip_emojis_and_replace_with_dots(c_lines[0]).rstrip('.،!؟: ')
            w = c_first.split()
            candidates.append(" ".join(w[:8]))
            
    best = candidates[0] if candidates else "یک جمله برای تو"
    best = best.rstrip('.،!؟: ')
    return best + "..."

def split_hook_into_lines(hook: str) -> list:
    hook_clean = hook.rstrip('.،!؟: ')
    words = hook_clean.split()
    if len(words) <= 4:
        return [hook_clean + "..."]
    
    mid = (len(words) + 1) // 2
    for i, w in enumerate(words):
        if '،' in w or ',' in w:
            if 2 <= i + 1 <= len(words) - 2:
                mid = i + 1
                break
                
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:]) + "..."
    return [line1, line2]

def logical_wrap_line(line: str, max_words_per_line: int = 7) -> list:
    """
    Intelligently breaks a long Persian line at logical phrasing points
    (commas, conjunctions like 'که', 'اما', 'ولی', 'تا', 'و') so text flows naturally.
    """
    words = line.split()
    if len(words) <= max_words_per_line:
        return [line]
        
    break_indices = []
    conjunctions = {"که", "اما", "ولی", "تا", "چون", "وقتی", "و"}
    
    for idx, w in enumerate(words):
        if idx == 0 or idx >= len(words) - 1:
            continue
        if '،' in w or ',' in w or ';' in w or '؛' in w:
            break_indices.append(idx + 1)
        elif w in conjunctions and 2 <= idx <= len(words) - 2:
            break_indices.append(idx)
            
    mid = len(words) // 2
    if break_indices:
        best_break = min(break_indices, key=lambda i: abs(i - mid))
        if 2 <= best_break <= len(words) - 2:
            return [" ".join(words[:best_break]), " ".join(words[best_break:])]
            
    return [" ".join(words[:mid]), " ".join(words[mid:])]

def parse_content_lines(content: str):
    """
    Splits content, removes emojis (replaces strictly with '...'), applies logical line breaks,
    and marks which parts (entire lines or specific words wrapped in == or **) get highlight colors.
    Respects deliberate user line formatting by preserving lines with <= 12 words.
    """
    cleaned_content = strip_emojis_and_replace_with_dots(content)
    raw_lines = [l.strip() for l in cleaned_content.split('\n') if l.strip()]
    if not raw_lines:
        return []
        
    # If content already has multiple deliberate lines (user formatted or poetic text),
    # do NOT aggressively split lines! Allow up to 12 words per line so deliberate linebreaks are preserved.
    # Only if content is in a dense, unformatted block (< 4 lines) do we break at 8 words.
    max_words = 12 if len(raw_lines) >= 4 else 8
    
    expanded_lines = []
    for l in raw_lines:
        sub_lines = logical_wrap_line(l, max_words_per_line=max_words)
        expanded_lines.extend(sub_lines)
        
    parsed = []
    total = len(expanded_lines)
    
    # Check if the user has provided explicit inline highlights anywhere
    has_explicit_hl = any("==" in l or "**" in l for l in expanded_lines)
    
    for idx, line in enumerate(expanded_lines):
        clean_line = line.strip()
        clean_line = re.sub(r'\.{2,}', '...', clean_line)
        
        # If user explicitly marked words with == or **, respect that exactly
        # If no explicit markers exist at all, fall back to auto-highlighting first and last lines
        is_full_line_hl = False
        if not has_explicit_hl:
            if idx == 0:
                is_full_line_hl = True
            elif idx == 1 and total > 5 and len(expanded_lines[0].split()) <= 4:
                is_full_line_hl = True
            elif idx >= total - 2 and total >= 4:
                is_full_line_hl = True
                
        parsed.append({"raw_line": clean_line, "full_line_highlight": is_full_line_hl})
        
    return parsed

def build_cover_html(hook_text: str, theme: str) -> str:
    """
    Cover styling: KEPT EXACTLY CONSTANT as original Figma template.
    Font: IRTitr, Normal weight (400), font-size: 90px (Light) / 95px (Dark).
    """
    bg_file = "light_cover.png" if theme == "light" else "dark_cover.png"
    b64_data = PLATES_BASE64.get(bg_file, "")
    
    lines = split_hook_into_lines(hook_text)
    lines_html = "".join([f"<div>{l}</div>" for l in lines])
    
    color = "#171717" if theme == "light" else "#FFF7ED"
    opacity = "0.85" if theme == "light" else "1.0"
    
    # Exact original Figma sizes & normal weight (constant as requested)
    font_size = "90px" if theme == "light" else "95px"
    line_height = "145px" if theme == "light" else "160px"
    
    b64_titr = FONTS_BASE64.get("IRTitr", "")
    src_titr = f"url('data:font/truetype;base64,{b64_titr}') format('truetype'), local('IRTitr')" if b64_titr else "local('IRTitr')"
    
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<style>
  @font-face {{
    font-family: 'IRTitr';
    src: {src_titr};
    font-weight: normal;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    position: relative;
    background-color: transparent;
  }}
  .card {{
    width: 1080px;
    height: 1920px;
    position: relative;
    background: url('data:image/png;base64,{b64_data}') center center no-repeat;
    background-size: cover;
  }}
  .hook-box {{
    position: absolute;
    top: 568px;
    left: 0;
    width: 1080px;
    text-align: center;
    font-family: 'IRTitr', sans-serif;
    font-weight: normal;
    font-size: {font_size};
    line-height: {line_height};
    color: {color};
    opacity: {opacity};
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="hook-box">
      {lines_html}
    </div>
  </div>
</body>
</html>"""

def build_text_post_html(content: str, theme: str, custom_styles: dict = None) -> str:
    """
    Text post styling: PROPERLY LARGER & BOLDER with real-time customization support.
    Font: IRLotus Bold (weight 900 or 400), customizable size, colors, and line highlights.
    Safe zone right: 195px.
    """
    custom_styles = custom_styles or {}
    bg_file = "light_text.png" if theme == "light" else "dark_text.png"
    b64_data = PLATES_BASE64.get(bg_file, "")
    
    parsed = parse_content_lines(content)
    n_lines = len(parsed)
    
    # Safe Bounding Box (Exact user Photoshop template: 806px width x 1308px height)
    # Canvas: 1080px x 1920px
    # Horizontal: Right margin 165px, Width 806px (leaves 109px left margin for Reels UI)
    # Vertical: Top safe bound 306px, Height 1308px, Bottom safe bound 1614px (leaves ~100px buffer before bottom emblem @ 1710px)
    right_margin = "165px"
    content_width = "806px"
    box_top_y = 306
    box_height_y = 1308
    box_bottom_y = 1614

    max_line_chars = max(len(it["raw_line"]) for it in parsed) if parsed else 0

    # Dynamic typography sizing strictly budgeted for the 806x1308 bounding box
    if n_lines <= 7:
        def_font_size = 64
        def_line_height = 106
    elif n_lines <= 9:
        def_font_size = 60
        def_line_height = 100
    elif n_lines <= 11:
        def_font_size = 57
        def_line_height = 94
    elif n_lines <= 13:
        def_font_size = 54
        def_line_height = 88
    elif n_lines <= 15:
        def_font_size = 50
        def_line_height = 80
    elif n_lines <= 17:
        def_font_size = 47
        def_line_height = 74
    else:
        def_font_size = 44
        def_line_height = 68

    # Prevent long lines from wrapping on 806px width
    if max_line_chars > 48 and def_font_size > 52:
        def_font_size = 52
        def_line_height = min(def_line_height, 86)
    if max_line_chars > 55 and def_font_size > 48:
        def_font_size = 48
        def_line_height = min(def_line_height, 78)

    # Apply user custom overrides if provided
    user_fs = custom_styles.get("font_size")
    font_size_val = int(user_fs) if user_fs and str(user_fs).isdigit() else def_font_size

    user_lh = custom_styles.get("line_height")
    if user_lh and str(user_lh).isdigit():
        line_height_val = int(user_lh)
    else:
        line_height_val = def_line_height if font_size_val == def_font_size else int(font_size_val * 1.62)

    # Usable height inside the 1308px box (budgeting 24px top & bottom safety padding = 1260px usable)
    max_usable_h = 1260
    if n_lines > 0 and (n_lines * line_height_val) > max_usable_h:
        line_height_val = max(52, max_usable_h // n_lines)
        font_size_val = min(font_size_val, int(line_height_val * 0.65))

    total_text_h = n_lines * line_height_val

    user_top = custom_styles.get("top_offset")
    is_custom_top = user_top is not None and str(user_top).lstrip("-").isdigit()

    if is_custom_top:
        req_top = int(user_top)
        max_allowed_top = max(box_top_y, box_bottom_y - total_text_h)
        min_allowed_top = box_top_y
        top_offset_val = max(min_allowed_top, min(req_top, max_allowed_top))
    else:
        # Default: Start directly at the ceiling of the safe bounding box (306px)
        top_offset_val = box_top_y

    justify_style = "flex-start"
    top_offset_css = f"{top_offset_val}px"
    max_height_css = f"{box_bottom_y - top_offset_val}px"

    font_size = f"{font_size_val}px"
    line_height = f"{line_height_val}px"

    is_bold = custom_styles.get("is_bold", True)
    if isinstance(is_bold, str):
        is_bold = is_bold.lower() in ("true", "1", "yes")
    font_weight = "bold" if is_bold else "normal"

    normal_color = "#242424" if theme == "light" else "#F1EFE8"
    
    # Custom highlight color override
    # Options: "default", "yellow" (#F4C466), "crimson" (#8B2635), "red" (#EF4444), "gold" (#EAB308)
    user_hl_color = custom_styles.get("hl_color")
    if user_hl_color == "yellow":
        hl_color = "#F4C466"
    elif user_hl_color == "crimson":
        hl_color = "#8B2635"
    elif user_hl_color == "red":
        hl_color = "#EF4444"
    elif user_hl_color and user_hl_color.startswith("#"):
        hl_color = user_hl_color
    else:
        hl_color = "#8B2635" if theme == "light" else "#F4C466"
    
    lines_html = ""
    for item in parsed:
        raw_l = item["raw_line"]
        if item.get("full_line_highlight"):
            # Whole line is highlighted
            clean_l = raw_l.replace("==", "").replace("**", "")
            lines_html += f'<div style="color: {hl_color}; margin-bottom: 2px;">{clean_l}</div>'
        else:
            # Check for inline highlight markers ==word== or **word**
            if "==" in raw_l or "**" in raw_l:
                # Replace ==text== or **text** with colored span
                formatted = re.sub(r'==([^=]+)==', rf'<span style="color: {hl_color}; font-weight: bold;">\1</span>', raw_l)
                formatted = re.sub(r'\*\*([^*]+)\*\*', rf'<span style="color: {hl_color}; font-weight: bold;">\1</span>', formatted)
                lines_html += f'<div style="color: {normal_color}; margin-bottom: 2px;">{formatted}</div>'
            else:
                lines_html += f'<div style="color: {normal_color}; margin-bottom: 2px;">{raw_l}</div>'
        
    b64_lotus_bold = FONTS_BASE64.get("IRLotusBold", "")
    b64_lotus_reg = FONTS_BASE64.get("IRLotus", "")
    src_bold = f"url('data:font/truetype;base64,{b64_lotus_bold}') format('truetype'), local('IRlotus-Bold')" if b64_lotus_bold else "local('IRlotus-Bold'), local('IRLotus Bold')"
    src_reg = f"url('data:font/truetype;base64,{b64_lotus_reg}') format('truetype'), local('IRLotus')" if b64_lotus_reg else "local('IRLotus'), local('IRlotus')"

    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<style>
  @font-face {{
    font-family: 'IRLotus';
    src: {src_bold};
    font-weight: 700;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'IRLotus';
    src: {src_bold};
    font-weight: 900;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'IRLotus';
    src: {src_bold};
    font-weight: bold;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'IRLotus';
    src: {src_reg};
    font-weight: 400;
    font-style: normal;
  }}
  @font-face {{
    font-family: 'IRLotus';
    src: {src_reg};
    font-weight: normal;
    font-style: normal;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    position: relative;
    background-color: transparent;
  }}
  .card {{
    width: 1080px;
    height: 1920px;
    position: relative;
    background: url('data:image/png;base64,{b64_data}') center center no-repeat;
    background-size: cover;
  }}
  /* Exact Safe Bounding Box (806px x 1308px): Right 165px, Top 306px to Bottom 1614px */
  .content-box {{
    position: absolute;
    top: {top_offset_css};
    right: {right_margin};
    width: {content_width};
    height: {max_height_css};
    max-height: {max_height_css};
    display: flex;
    flex-direction: column;
    justify-content: {justify_style};
    overflow: hidden;
    box-sizing: border-box;
    font-family: 'IRLotus', sans-serif;
    font-weight: {font_weight};
    font-size: {font_size};
    line-height: {line_height};
    text-align: right;
    letter-spacing: -0.2px;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="content-box">
      {lines_html}
    </div>
  </div>
</body>
</html>"""

def render_html_to_file(browser_exe: str, html_str: str, out_png: str):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as f:
        f.write(html_str)
        temp_html = f.name
        
    try:
        cmd = [
            browser_exe,
            "--headless=new",
            "--disable-gpu",
            f"--screenshot={out_png}",
            "--window-size=1080,1920",
            "--hide-scrollbars",
            "--default-background-color=00000000",
            temp_html
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    finally:
        if os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except:
                pass

def render_preview_png_bytes(slot: int = 1, date_str: str = None, item_type: str = "text",
                             custom_hook: str = None, custom_content: str = None,
                             custom_style: dict = None, theme_override: str = None) -> bytes:
    """
    Renders either the cover PNG or text graphic PNG in-memory without saving any file to disk,
    returning raw PNG bytes for direct browser preview.
    """
    browser = get_browser_executable()
    if not browser:
        raise RuntimeError("Google Chrome or Microsoft Edge not found on this system.")

    slot = int(slot)
    theme = theme_override or get_slot_theme(slot)
    custom_style = custom_style or {}

    hook = (custom_hook or "").strip()
    content = (custom_content or "").strip()

    if not hook or not content:
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            scripts = db.get("scripts", [])
            day_scripts = {int(s.get("scheduled_slot")): s for s in scripts if s.get("scheduled_date") == date_str and s.get("scheduled_slot")}
            script = day_scripts.get(slot)
            if script:
                if not hook:
                    hook = clean_hook_text(script.get("hook"), script.get("title"), script.get("content"))
                if not content:
                    content = script.get("content", "")
        except Exception:
            pass

    if not hook:
        hook = f"هوک تستی اسلات {slot}"
    if not content:
        content = f"متن نمونه تکست‌گرافی برای پیش‌نمایش اسلات {slot}..."

    if item_type.lower() == "cover":
        html_str = build_cover_html(hook, theme)
    else:
        html_str = build_text_post_html(content, theme, custom_styles=custom_style)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as f:
        f.write(html_str)
        temp_html = f.name

    with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as f_out:
        temp_png = f_out.name

    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            f"--screenshot={temp_png}",
            "--window-size=1080,1920",
            "--hide-scrollbars",
            "--default-background-color=00000000",
            temp_html
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        with open(temp_png, "rb") as fp:
            return fp.read()
    finally:
        for p in [temp_html, temp_png]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

def generate_daily_posts(date_str: str = None, target_folder: str = None, custom_hooks: dict = None, generate_videos: bool = False, custom_audios: dict = None, custom_styles: dict = None):
    browser = get_browser_executable()
    if not browser:
        raise RuntimeError("Google Chrome or Microsoft Edge not found on this system.")
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    scripts = db.get("scripts", [])
    
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    day_scripts = {int(s.get("scheduled_slot")): s for s in scripts if s.get("scheduled_date") == date_str and s.get("scheduled_slot")}
    
    if not day_scripts:
        raise ValueError(f"No scheduled scripts found in database for date: {date_str}")
        
    if not target_folder:
        import jdatetime
        parts = [int(p) for p in date_str.split("-")]
        j_date = jdatetime.date.fromgregorian(year=parts[0], month=parts[1], day=parts[2])
        folder_name = j_date.strftime("%Y-%m-%d")
        target_folder = os.path.join(r"D:\زر تکست", folder_name)
        
    os.makedirs(target_folder, exist_ok=True)
    
    custom_hooks = custom_hooks or {}
    custom_audios = custom_audios or {}
    custom_styles = custom_styles or {}
    catalog = get_soundtracks_catalog()
    
    results = []
    
    for slot in range(1, 7):
        script = day_scripts.get(slot)
        if not script:
            continue
            
        slot_style = custom_styles.get(str(slot)) or custom_styles.get(slot) or {}
        theme = slot_style.get("theme") or get_slot_theme(slot)
        if theme not in ("light", "dark"):
            theme = get_slot_theme(slot)
        
        if str(slot) in custom_hooks and custom_hooks[str(slot)].strip():
            hook = custom_hooks[str(slot)].strip()
        elif slot in custom_hooks and custom_hooks[slot].strip():
            hook = custom_hooks[slot].strip()
        else:
            hook = clean_hook_text(script.get("hook"), script.get("title"), script.get("content"))
            
        cover_filename = f"post - {slot} - cover.png"
        text_filename = f"post - {slot} - text.png"
        cover_path = os.path.join(target_folder, cover_filename)
        text_path = os.path.join(target_folder, text_filename)
        
        # 1. Render Cover (CONSTANT Figma standard sizing & weight)
        c_html = build_cover_html(hook, theme)
        render_html_to_file(browser, c_html, cover_path)
        
        # 2. Render Text (PROPERLY LARGER & BOLDER with safe zone & user styles)
        slot_style = custom_styles.get(str(slot)) or custom_styles.get(slot) or {}
        # If user edited the text content directly in preview
        post_content = slot_style.get("content") or script.get("content", "")
        t_html = build_text_post_html(post_content, theme, slot_style)
        render_html_to_file(browser, t_html, text_path)
        
        item_res = {
            "slot": slot,
            "theme": theme,
            "title": script.get("title"),
            "hook": hook,
            "cover_file": cover_filename,
            "cover_size": os.path.getsize(cover_path) if os.path.exists(cover_path) else 0,
            "text_file": text_filename,
            "text_size": os.path.getsize(text_path) if os.path.exists(text_path) else 0,
            "video_file": None,
            "video_size": 0
        }
        
        # 3. Optional Video Generation (ffmpeg MP4)
        if generate_videos:
            video_filename = f"post - {slot}.mp4"
            video_path = os.path.join(target_folder, video_filename)
            
            # Determine audio track
            audio_candidate = None
            if str(slot) in custom_audios and custom_audios[str(slot)]:
                audio_candidate = custom_audios[str(slot)]
            elif slot in custom_audios and custom_audios[slot]:
                audio_candidate = custom_audios[slot]
            else:
                # Fallback to slot archetype from catalog
                # Default slot to archetype mapping:
                # Slot 1: Archetype 5 (Manifest / Authenticity)
                # Slot 2: Archetype 3 (Safe Person / Short Story)
                # Slot 3: Archetype 4 (Relationship Grievance)
                # Slot 4: Archetype 4 (Psychological Independence)
                # Slot 5: Archetype 5 (Night Peak Manifest)
                # Slot 6: Archetype 1 (Strong Silent / Farewell)
                slot_to_arch = {1: 5, 2: 3, 3: 4, 4: 4, 5: 5, 6: 1}
                arch_num = str(slot_to_arch.get(slot, 1))
                arch_tracks = catalog.get("archetypes", {}).get(arch_num, [])
                if arch_tracks:
                    audio_candidate = os.path.join(BASE_DIR, arch_tracks[0].get("relative_path"))
                    
            if audio_candidate and not os.path.isabs(audio_candidate):
                audio_candidate = os.path.join(BASE_DIR, audio_candidate)
                
            v_ok = generate_post_video(text_path, audio_candidate, video_path)
            if v_ok:
                item_res["video_file"] = video_filename
                item_res["video_size"] = os.path.getsize(video_path)
                
        results.append(item_res)
        
    return {
        "status": "success",
        "date": date_str,
        "target_folder": target_folder,
        "total_posts": len(results),
        "total_images": len(results) * 2,
        "total_videos": sum(1 for r in results if r.get("video_file")),
        "items": results
    }

def generate_single_post(slot: int, date_str: str = None, target_folder: str = None, custom_hook: str = None, generate_video: bool = True, custom_audio: str = None, custom_style: dict = None):
    """
    Instantly generates/regenerates a single slot's cover, text graphic, and optional MP4 video
    in 2-4 seconds without touching the other 5 slots.
    """
    browser = get_browser_executable()
    if not browser:
        raise RuntimeError("Google Chrome or Microsoft Edge not found on this system.")
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    scripts = db.get("scripts", [])
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    day_scripts = {int(s.get("scheduled_slot")): s for s in scripts if s.get("scheduled_date") == date_str and s.get("scheduled_slot")}
    script = day_scripts.get(int(slot))
    if not script:
        raise ValueError(f"No scheduled script found for slot {slot} on date {date_str}")
        
    if not target_folder:
        import jdatetime
        parts = [int(p) for p in date_str.split("-")]
        j_date = jdatetime.date.fromgregorian(year=parts[0], month=parts[1], day=parts[2])
        folder_name = j_date.strftime("%Y-%m-%d")
        target_folder = os.path.join(r"D:\زر تکست", folder_name)
        
    os.makedirs(target_folder, exist_ok=True)
    
    custom_style = custom_style or {}
    catalog = get_soundtracks_catalog()
    theme = custom_style.get("theme") or get_slot_theme(int(slot))
    if theme not in ("light", "dark"):
        theme = get_slot_theme(int(slot))
    
    if custom_hook and custom_hook.strip():
        hook = custom_hook.strip()
    else:
        hook = clean_hook_text(script.get("hook"), script.get("title"), script.get("content"))
        
    cover_filename = f"post - {slot} - cover.png"
    text_filename = f"post - {slot} - text.png"
    cover_path = os.path.join(target_folder, cover_filename)
    text_path = os.path.join(target_folder, text_filename)
    
    # 1. Render Cover
    c_html = build_cover_html(hook, theme)
    render_html_to_file(browser, c_html, cover_path)
    
    # 2. Render Text
    post_content = custom_style.get("content") or script.get("content", "")
    t_html = build_text_post_html(post_content, theme, custom_style)
    render_html_to_file(browser, t_html, text_path)
    
    item_res = {
        "slot": int(slot),
        "theme": theme,
        "title": script.get("title"),
        "hook": hook,
        "cover_file": cover_filename,
        "cover_path": cover_path,
        "cover_size": os.path.getsize(cover_path) if os.path.exists(cover_path) else 0,
        "text_file": text_filename,
        "text_path": text_path,
        "text_size": os.path.getsize(text_path) if os.path.exists(text_path) else 0,
        "video_file": None,
        "video_path": None,
        "video_size": 0
    }
    
    if generate_video:
        video_filename = f"post - {slot}.mp4"
        video_path = os.path.join(target_folder, video_filename)
        
        audio_candidate = custom_audio
        if not audio_candidate:
            slot_to_arch = {1: 5, 2: 3, 3: 4, 4: 4, 5: 5, 6: 1}
            arch_num = str(slot_to_arch.get(int(slot), 1))
            arch_tracks = catalog.get("archetypes", {}).get(arch_num, [])
            if arch_tracks:
                audio_candidate = os.path.join(BASE_DIR, arch_tracks[0].get("relative_path"))
                
        if audio_candidate and not os.path.isabs(audio_candidate):
            audio_candidate = os.path.join(BASE_DIR, audio_candidate)
            
        v_ok = generate_post_video(text_path, audio_candidate, video_path)
        if v_ok:
            item_res["video_file"] = video_filename
            item_res["video_path"] = video_path
            item_res["video_size"] = os.path.getsize(video_path)
            
    return {
        "status": "success",
        "date": date_str,
        "target_folder": target_folder,
        "item": item_res
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    print(f"Executing Post Maker for {today_str}...")
    res = generate_daily_posts(today_str)
    print(f"Generated {res['total_images']} images successfully into {res['target_folder']}")
