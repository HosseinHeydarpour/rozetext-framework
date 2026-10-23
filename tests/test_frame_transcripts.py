import json
import os
import re
import sys
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")
VERIFIED_PATH = os.path.join(BASE_DIR, "data", "verified_frame_transcripts.json")

def test_verified_transcripts_exist():
    assert os.path.exists(VERIFIED_PATH), "verified_frame_transcripts.json must exist"
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 10, "Should have at least 10 verified frame transcripts"

def test_thursday_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    thu_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-15"}
    
    # Check slots 2, 3, 4, 5, 6
    expected_shortcodes = {
        2: "Dcv6DdWslEP",
        3: "Dc2HRKMCgDE",
        4: "DdzA7ApRmNo",
        5: "DdeEAi4Ne3y",
        6: "Ddrao3dum5f"
    }
    
    for slot, code in expected_shortcodes.items():
        assert slot in thu_scripts, f"Thursday slot {slot} must exist"
        script = thu_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified dictionary"
        v = verified[code]
        assert script["content"] == v["content"], f"Thursday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Thursday slot {slot} raw text must match verified verbatim text"

def test_friday_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    fri_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-16"}
    expected_shortcodes = {
        1: "Dc8HwGyOQJS",
        2: "DdjJJxbMM6f",
        3: "DdCtdp3CHT0",
        4: "DGyXN3fRYFl",
        5: "Dbx5dsaJNJ1",
        6: "DcRrYXESCEI"
    }

    for slot, code in expected_shortcodes.items():
        assert slot in fri_scripts, f"Friday slot {slot} must exist"
        script = fri_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified dictionary"
        v = verified[code]
        assert script["content"] == v["content"], f"Friday slot {slot} content must match verified verbatim text exactly"

def test_monday_all_6_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    mon_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-19"}
    expected_monday = {
        1: ("DZId7nxNc_K", "وجدان راحتم زندگی سختمو آسون تر کرد"),
        2: ("DeZH7Z0u1s6", "من متهم ردیف اول زندگی خودمم"),
        3: ("Dc_z1QtMhd7", "بعضی وقتا واقعاً نمی‌دونم از چی خستم"),
        4: ("DbjHTCAMKq8", "گاهی با خودم فکر می‌کنم"),
        5: ("DbbY_s-MMK0", "کاش یکی موقع بزرگ شدن بهمون می‌گفت"),
        6: ("DeeBHT_O_Zi", "حلال نمیکنم...")
    }

    for slot, (code, title_prefix) in expected_monday.items():
        assert slot in mon_scripts, f"Monday slot {slot} must exist in scripts-db"
        script = mon_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified_frame_transcripts.json"
        v = verified[code]
        assert script["content"] == v["content"], f"Monday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Monday slot {slot} raw text must match verified verbatim text"
        assert script.get("frame_transcript_verified") is True, f"Monday slot {slot} must have frame_transcript_verified=True"
        
        frame_file = os.path.join(BASE_DIR, "downloads", "frames", f"{code}_frame.png")
        assert os.path.exists(frame_file), f"Frame image for {code} must exist on disk: {frame_file}"
        assert os.path.getsize(frame_file) > 1000, f"Frame image for {code} must be a valid non-empty image"

def test_tuesday_all_6_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    tue_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-20"}
    expected_tuesday = {
        1: "DblsFKUsRjn",
        2: "Dbd9tTKMOsp",
        3: "DcHKsdUMpGH",
        4: "Dbv_TqKMl-P",
        5: "Dcy79eFObfp",
        6: "Dc1S6FRoBRz"
    }

    for slot, code in expected_tuesday.items():
        assert slot in tue_scripts, f"Tuesday slot {slot} must exist in scripts-db"
        script = tue_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified_frame_transcripts.json"
        v = verified[code]
        assert script["content"] == v["content"], f"Tuesday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Tuesday slot {slot} raw text must match verified verbatim text"
        assert script.get("frame_transcript_verified") is True, f"Tuesday slot {slot} must have frame_transcript_verified=True"
        
        frame_file = os.path.join(BASE_DIR, "downloads", "frames", f"{code}_frame.png")
        assert os.path.exists(frame_file), f"Frame image for {code} must exist on disk: {frame_file}"
        assert os.path.getsize(frame_file) > 1000, f"Frame image for {code} must be a valid non-empty image"

def test_wednesday_all_6_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    wed_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-21"}
    expected_wednesday = {
        1: "Da8duzdMYQt",
        2: "DaOCORNMENF",
        3: "Da0ofrisUtb",
        4: "DR7fbNlCBle",
        5: "DayDs66sKNZ",
        6: "DRpeLe-iMDr"
    }

    for slot, code in expected_wednesday.items():
        assert slot in wed_scripts, f"Wednesday slot {slot} must exist in scripts-db"
        script = wed_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified_frame_transcripts.json"
        v = verified[code]
        assert script["content"] == v["content"], f"Wednesday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Wednesday slot {slot} raw text must match verified verbatim text"
        assert script.get("frame_transcript_verified") is True, f"Wednesday slot {slot} must have frame_transcript_verified=True"
        
        frame_file = os.path.join(BASE_DIR, "downloads", "frames", f"{code}_frame.png")
        assert os.path.exists(frame_file), f"Frame image for {code} must exist on disk: {frame_file}"
        assert os.path.getsize(frame_file) > 1000, f"Frame image for {code} must be a valid non-empty image"

def test_thursday_2026_10_22_all_6_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    thu_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-22"}
    expected_thursday = {
        1: "DdeYIgZqlG9",
        2: "DdhIZDEK8_S",
        3: "Ddop_U4RDVl",
        4: "DanaKZYN_9w",
        5: "DdotWXnCiBy",
        6: "DZiJyf3ImZl"
    }

    for slot, code in expected_thursday.items():
        assert slot in thu_scripts, f"Thursday 2026-10-22 slot {slot} must exist in scripts-db"
        script = thu_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified_frame_transcripts.json"
        v = verified[code]
        assert script["content"] == v["content"], f"Thursday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Thursday slot {slot} raw text must match verified verbatim text"
        assert script.get("frame_transcript_verified") is True, f"Thursday slot {slot} must have frame_transcript_verified=True"
        
        frame_file = os.path.join(BASE_DIR, "downloads", "frames", f"{code}_frame.png")
        assert os.path.exists(frame_file), f"Frame image for {code} must exist on disk: {frame_file}"
        assert os.path.getsize(frame_file) > 1000, f"Frame image for {code} must be a valid non-empty image"

def test_friday_2026_10_23_all_6_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    fri_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-23"}
    expected_friday = {
        1: "Ded4vxjsQX3",
        2: "DeHxCX3i3xc",
        3: "DI_5NgqITTy",
        4: "DIO_li0IL5X",
        5: "DKaDbPWoKWC",
        6: "DdzFv9hCAZO"
    }

    for slot, code in expected_friday.items():
        assert slot in fri_scripts, f"Friday 2026-10-23 slot {slot} must exist in scripts-db"
        script = fri_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified_frame_transcripts.json"
        v = verified[code]
        assert script["content"] == v["content"], f"Friday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Friday slot {slot} raw text must match verified verbatim text"
        assert script.get("frame_transcript_verified") is True, f"Friday slot {slot} must have frame_transcript_verified=True"
        
        frame_file = os.path.join(BASE_DIR, "downloads", "frames", f"{code}_frame.png")
        assert os.path.exists(frame_file), f"Frame image for {code} must exist on disk: {frame_file}"
        assert os.path.getsize(frame_file) > 1000, f"Frame image for {code} must be a valid non-empty image"

def test_saturday_2026_10_24_all_6_slots_match_verified_frames():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)

    sat_scripts = {s["scheduled_slot"]: s for s in db["scripts"] if s.get("scheduled_date") == "2026-10-24"}
    expected_saturday = {
        1: "DPHRC0yCJxg",
        2: "DK-E6xoonsH",
        3: "DbyY0F7tmAn",
        4: "DZSr1vMN1mr",
        5: "DcjQOwtN86T",
        6: "DcJelWZKk0u"
    }

    for slot, code in expected_saturday.items():
        assert slot in sat_scripts, f"Saturday 2026-10-24 slot {slot} must exist in scripts-db"
        script = sat_scripts[slot]
        assert code in verified, f"Shortcode {code} must be in verified_frame_transcripts.json"
        v = verified[code]
        assert script["content"] == v["content"], f"Saturday slot {slot} content must match verified verbatim text exactly"
        assert script["extracted_raw_text"] == v["content"], f"Saturday slot {slot} raw text must match verified verbatim text"
        assert script.get("frame_transcript_verified") is True, f"Saturday slot {slot} must have frame_transcript_verified=True"
        
        frame_file = os.path.join(BASE_DIR, "downloads", "frames", f"{code}_frame.png")
        assert os.path.exists(frame_file), f"Frame image for {code} must exist on disk: {frame_file}"
        assert os.path.getsize(frame_file) > 1000, f"Frame image for {code} must be a valid non-empty image"

def test_fidelity_auditor_catches_hallucination():
    from scripts.verify_reel_transcript import audit_script_fidelity
    
    # 1. Hallucinated script (the old wrong Monday Slot 1 text)
    fake_script = {
        "id": "test-fake",
        "title": "وجدان راحتم زندگی سختمو آسون تر کرد",
        "source_url": "https://www.instagram.com/reel/DZId7nxNc_K/",
        "is_viral_hunted": True,
        "content": "وجدان راحتم زندگی سختمو آسون تر کرد\nخیلیا بهم ضربه زدن اما به هیچکس ضربه نزدم\nخیلی جاها از حقم گذشتم...",
        "extracted_raw_text": "خیلیا بهم ضربه زدن..."
    }
    audit_res = audit_script_fidelity(fake_script)
    assert audit_res["severity"] == "CRITICAL", "Auditor MUST flag hallucinated text as CRITICAL"
    assert any("مغایرت قطعی با فریم تاییدشده" in f for f in audit_res["findings"]), "Findings must report exact frame mismatch"

    # 2. Verbatim verified script
    with open(VERIFIED_PATH, "r", encoding="utf-8") as f:
        verified = json.load(f)
    v_text = verified["DZId7nxNc_K"]["content"]
    clean_script = {
        "id": "test-clean",
        "title": "وجدان راحتم زندگی سختمو آسون تر کرد",
        "source_url": "https://www.instagram.com/reel/DZId7nxNc_K/",
        "is_viral_hunted": True,
        "content": v_text,
        "extracted_raw_text": v_text
    }
    clean_res = audit_script_fidelity(clean_script)
    assert clean_res["severity"] == "OK", "Auditor must approve verbatim matching script with OK severity"


