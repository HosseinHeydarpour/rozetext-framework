import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")

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

def audit_script_for_caption_trap(script: dict) -> dict:
    """
    Checks if a script text suffers from the Caption Trap (containing caption fluff
    or being too short while claiming high views).
    """
    content = script.get("content", "")
    raw = script.get("extracted_raw_text", "")
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    words = content.split()
    
    findings = []
    
    # Check for caption patterns
    for pat in CAPTION_TRAP_PATTERNS:
        if re.search(pat, content):
            findings.append(f"یافتن عبارت مشکوک کپشن: {pat}")
            
    # Check length
    if len(lines) < 6 and script.get("is_viral_hunted", False):
        findings.append(f"تعداد خطوط کم است ({len(lines)} سطر). احتمال تلخیص یا برداشت کپشن ناقص وجود دارد.")
        
    if len(words) < 40 and script.get("is_viral_hunted", False):
        findings.append(f"تعداد کلمات کم است ({len(words)} کلمه).")
        
    is_clean = len(findings) == 0
    return {
        "id": script.get("id"),
        "title": script.get("title"),
        "lines_count": len(lines),
        "words_count": len(words),
        "is_clean": is_clean,
        "findings": findings
    }

def audit_all_pending_scripts():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return
        
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        
    pending = [s for s in db.get("scripts", []) if not s.get("published", False)]
    print(f"Auditing {len(pending)} pending scripts for Caption Trap / Incomplete Text...\n")
    
    issues_found = 0
    for s in pending:
        result = audit_script_for_caption_trap(s)
        if not result["is_clean"]:
            issues_found += 1
            print(f"⚠️ [ISSUE] Script {s.get('id')} ({s.get('title')[:40]}):")
            for f in result["findings"]:
                print(f"   - {f}")
        else:
            print(f"✅ [OK] Script {s.get('id')} ({result['lines_count']} lines, {result['words_count']} words): {s.get('title')[:35]}")
            
    print(f"\nAudit complete. Issues found: {issues_found}/{len(pending)}")

if __name__ == "__main__":
    audit_all_pending_scripts()
