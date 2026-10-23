import json
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")
VERIFIED_PATH = os.path.join(BASE_DIR, "data", "verified_frame_transcripts.json")

def load_verified_transcripts():
    if os.path.exists(VERIFIED_PATH):
        try:
            with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def audit_script_for_caption_trap(script: dict) -> dict:
    content = script.get("content", "")
    raw = script.get("extracted_raw_text", "")
    text_to_check = raw if raw else content
    findings = []
    for pat in CAPTION_TRAP_PATTERNS:
        if re.search(pat, text_to_check):
            findings.append(f"تله کپشن: عبارت کپشنی یافت شد ({pat}).")
    return {
        "is_clean": len(findings) == 0,
        "findings": findings
    }

# 1. Caption trap phrases
CAPTION_TRAP_PATTERNS = [
    r"نظرتون\s+رفقا",
    r"شما\s+هم\s*[\?؟]",
    r"برام\s+بنویسید",
    r"کامنت\s+کنید",
    r"خوش\s*بیان\s*✍",
    r"حضورتون\s+دلگرمیمه",
    r"ممنون\s+کنارمین",
    r"#\w+",
    r"ادامه\s+در\s+کپشن"
]

# 2. Known LLM autocomplete / hallucination clichés
HALLUCINATION_CLICHES = [
    ("بخشش مال آدماست", "کلیشه معروف توییتر درباره بخشش و فراموشی"),
    ("فراموش کردن کار خداست", "کلیشه معروف توییتر درباره فراموشی"),
    ("زیر پتو", "کلیشه گریه زیر پتو"),
    ("من خدا نیستم", "کلیشه پایان‌بندی خیانت"),
    ("دستام یخ زده بود و پاهام", "توصیف فیزیکی اغراق‌آمیز هوش مصنوعی"),
    ("قلبم هزار تیکه شد", "کلیشه اغراق‌آمیز دل‌شکستگی"),
]

def find_local_frame(shortcode: str) -> str:
    if not shortcode:
        return None
    patterns = [
        os.path.join(BASE_DIR, "downloads", "frames", f"*{shortcode}*.png"),
        os.path.join(BASE_DIR, "downloads", "frames", f"*{shortcode}*.jpg"),
        os.path.join(BASE_DIR, "assets", "hunted_frames", f"*{shortcode}*.png"),
        os.path.join(BASE_DIR, "assets", "hunted_frames", f"*{shortcode}*.jpg"),
    ]
    for pat in patterns:
        matches = glob.glob(pat)
        if matches and os.path.exists(matches[0]):
            return matches[0]
    return None

def find_local_audio(shortcode: str) -> str:
    if not shortcode:
        return None
    patterns = [
        os.path.join(BASE_DIR, "downloads", "reels", f"*{shortcode}*.mp3"),
        os.path.join(BASE_DIR, "downloads", "reels", f"*{shortcode}*.m4a"),
        os.path.join(BASE_DIR, "downloads", "reels", f"*{shortcode}*.wav"),
    ]
    for pat in patterns:
        matches = glob.glob(pat)
        if matches and os.path.exists(matches[0]):
            return matches[0]
    return None

def audit_script_fidelity(script: dict) -> dict:
    content = script.get("content", "")
    raw = script.get("extracted_raw_text", "")
    text_to_check = raw if raw else content
    lines = [line.strip() for line in text_to_check.splitlines() if line.strip()]
    words = text_to_check.split()
    
    source_url = script.get("source_url", "")
    m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", source_url)
    shortcode = m.group(1) if m else None
    
    frame_path = find_local_frame(shortcode)
    audio_path = find_local_audio(shortcode) if "find_local_audio" in globals() else None
    is_hunted = script.get("is_viral_hunted", False)
    is_declamation = script.get("is_declamation_transcript", False)
    
    findings = []
    severity = "OK"  # OK, WARNING, CRITICAL
    
    # Check media existence for hunted reels
    if is_hunted:
        if is_declamation:
            if not audio_path and not frame_path:
                findings.append("⚠️ فایل صوتی یا فریم ویدیوی دکلمه روی سیستم دانلود نشده است.")
                if severity != "CRITICAL":
                    severity = "WARNING"
        else:
            if not frame_path:
                findings.append("⚠️ فریم ویدیوی مرجع روی سیستم دانلود نشده است (ریسک عدم انطباق با واقعیت).")
                if severity != "CRITICAL":
                    severity = "WARNING"

    # Verbatim match check against verified frame transcripts
    verified_db = load_verified_transcripts()
    if shortcode and shortcode in verified_db:
        v_content = verified_db[shortcode].get("content", "").strip()
        def norm(t):
            return re.sub(r"\s+", " ", t).replace("\u200c", "").replace("ي", "ی").replace("ك", "ک").strip()
        if norm(text_to_check) != norm(v_content):
            findings.append(f"🚨 مغایرت قطعی با فریم تاییدشده ({shortcode}): متن ثبت‌شده با متن استخراج‌شده از ویدیوی مرجع مطابقت ندارد.")
            severity = "CRITICAL"
                
    # Check for caption trap patterns
    for pat in CAPTION_TRAP_PATTERNS:
        if re.search(pat, text_to_check):
            findings.append(f"تله کپشن: عبارت کپشنی یافت شد ({pat}).")
            severity = "CRITICAL"
            
    # Check for hallucination clichés
    for cliché, desc in HALLUCINATION_CLICHES:
        if cliché in text_to_check:
            findings.append(f"🚨 هشدار توهم هوش مصنوعی: عبارت کلیشه‌ای مشکوک یافت شد («{cliché}» — {desc}).")
            severity = "CRITICAL"
            
    # Check minimum length for hunted reels
    if is_hunted:
        if len(lines) < 6:
            findings.append(f"تعداد خطوط کم است ({len(lines)} سطر). احتمال تلخیص ناقص متن ویدیو.")
            if severity != "CRITICAL":
                severity = "WARNING"
        if len(words) < 40:
            findings.append(f"تعداد کلمات کم است ({len(words)} کلمه).")
            if severity != "CRITICAL":
                severity = "WARNING"
                
    return {
        "id": script.get("id"),
        "title": script.get("title"),
        "shortcode": shortcode,
        "is_hunted": is_hunted,
        "has_frame": bool(frame_path),
        "frame_path": frame_path,
        "lines_count": len(lines),
        "words_count": len(words),
        "severity": severity,
        "findings": findings
    }

def audit_all_scripts(only_pending: bool = True):
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    target_scripts = db.get("scripts", [])
    if only_pending:
        target_scripts = [s for s in target_scripts if not s.get("published", False)]
        
    print(f"============================================================")
    print(f"🔍 ممیزی جامع دقت استخراج و تطابق فریم ریلزها ({len(target_scripts)} اسکریپت)")
    print(f"============================================================\n")
    
    crit_count = 0
    warn_count = 0
    ok_count = 0
    
    for s in target_scripts:
        res = audit_script_fidelity(s)
        sev = res["severity"]
        title_disp = (s.get("title") or "بدون عنوان")[:40]
        
        if sev == "CRITICAL":
            crit_count += 1
            print(f"🚨 [CRITICAL] {s.get('id')} — {title_disp}")
            for f in res["findings"]:
                print(f"    ❌ {f}")
            print()
        elif sev == "WARNING":
            warn_count += 1
            print(f"⚠️ [WARNING] {s.get('id')} — {title_disp}")
            for f in res["findings"]:
                print(f"    🔸 {f}")
            print()
        else:
            ok_count += 1
            frame_status = "🖼️ فریم تاییدشده" if res["has_frame"] else "✨ تولید AI"
            # print(f"✅ [OK] {s.get('id')} ({frame_status}): {title_disp}")
            
    print(f"------------------------------------------------------------")
    print(f"📊 خلاصه بازرسی:")
    print(f"  ✅ بدون مشکل و تاییدشده (OK): {ok_count}")
    print(f"  ⚠️ نیازمند بررسی فریم (WARNING): {warn_count}")
    print(f"  🚨 مغایرت بحرانی یا توهم مدل (CRITICAL): {crit_count}")
    print(f"============================================================\n")

if __name__ == "__main__":
    audit_all_scripts(only_pending=False)
