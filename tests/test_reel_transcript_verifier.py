import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.verify_reel_transcript import audit_script_for_caption_trap, DB_PATH

class TestReelTranscriptVerifier(unittest.TestCase):
    def test_caption_trap_detection(self):
        # A fake trap script with caption fluff
        fake_trap = {
            "id": "fake-001",
            "title": "تست تله کپشن",
            "is_viral_hunted": True,
            "content": "نظرتون رفقا ؟ شما هم اینطورید ؟\nمن اگه کنار کسی بودم برای خودش بوده ..\nوحیدرضا خوش بیان ✍🏻",
            "extracted_raw_text": "نظرتون رفقا ؟ شما هم ؟"
        }
        res = audit_script_for_caption_trap(fake_trap)
        self.assertFalse(res["is_clean"], "Caption trap must be detected!")
        self.assertGreater(len(res["findings"]), 0)

    def test_clean_verbatim_script(self):
        # A clean verbatim script with full lines
        clean_script = {
            "id": "clean-001",
            "title": "تست متن کامل",
            "is_viral_hunted": True,
            "content": (
                "حال عجیبی دارم ..\n"
                "نه اونقدر غمگینم که نتونم ادامه بدم ،\n"
                "نه اونقدر حالم خوبه که ذوق چیزی رو داشته باشم .\n"
                "من این روزا بین آدمی که\n"
                "میخواد زندگیو جدی بگیره و آدمی که میخواد\n"
                "همه چیو رها کنه معلقم ، خیلی معلق ..\n"
                "نه حوصله توضیح دادن دارم\n"
                "نه توان بحث کردن .\n"
                "فقط یه گوشه ایستادم و دارم نگاه میکنم\n"
                "که روزا چطور میان و میرن .."
            ),
            "extracted_raw_text": "همان متن"
        }
        res = audit_script_for_caption_trap(clean_script)
        self.assertTrue(res["is_clean"], "Verbatim script must pass clean audit!")

    def test_database_today_slot5_and_slot6(self):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        slot5 = next((s for s in db["scripts"] if s["id"] == "script-1791049793923-051"), None)
        self.assertIsNotNone(slot5)
        self.assertIn("من هیچوقت هیچ آدمی رو برای منفعت", slot5["content"])
        self.assertIn("آدمی که با دلش زندگی میکنه نه با حساب کتاباش", slot5["content"])
        self.assertEqual(len(slot5["content"].splitlines()), 11)

        slot6 = next((s for s in db["scripts"] if s["id"] == "script-1791049794088-053"), None)
        self.assertIsNotNone(slot6)
        self.assertIn("حال عجیبی دارم", slot6["content"])
        self.assertIn("هم تنهایی اذیتم میکنه هم حضور آدما", slot6["content"])
        self.assertIn("همه چیو رها کنه معلقم ، خیلی معلق ..", slot6["content"])
        self.assertEqual(len(slot6["content"].splitlines()), 8)

if __name__ == "__main__":
    unittest.main()
