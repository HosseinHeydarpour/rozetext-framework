import json
import os
import shutil
import tempfile
import unittest

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import PublisherEngine, DAILY_6_SLOTS, get_date_slot_info


class TestPublisherAppAndHistorySync(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "scripts-db.json")
        self.root_hist = os.path.join(self.temp_dir, "published-content-history.md")
        self.skill_hist = os.path.join(self.temp_dir, "skill-published-content-history.md")

        # Copy the real published-content-history.md into temp_dir so we test against the real 233-reel file!
        real_hist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "published-content-history.md")
        shutil.copyfile(real_hist, self.root_hist)
        shutil.copyfile(real_hist, self.skill_hist)

        self.engine = PublisherEngine(
            db_path=self.db_path,
            root_history_path=self.root_hist,
            skill_history_path=self.skill_hist
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_add_and_schedule_6_daily_slots(self):
        """Verify adding 6 scripts assigns all 6 distinct optimal daily time slots (1..6) and weekday insights."""
        # 2026-10-02 is a Friday (Peak day: 17,682 online followers in slot 5)
        friday_date = "2026-10-02"
        archetypes = [
            "آرکتایپ ۱: آدم همیشه قوی",
            "آرکتایپ ۲: خداحافظی باوقار",
            "آرکتایپ ۳: تقدیم به آدم امن",
            "آرکتایپ ۴: گلایه بی‌دفاع",
            "آرکتایپ ۵: مانیفست اصالت",
            "آرکتایپ ۶: مینی‌روایت دیالوگی",
        ]
        for idx, arch in enumerate(archetypes, 1):
            self.engine.add_script({
                "id": f"test-s-{idx}",
                "title": f"تست {idx}",
                "archetype": arch,
                "content": f"خط اول تست {idx}\nخط دوم تست\nخط پایانی تست {idx}",
                "caption": f"کپشن تست {idx}",
                "scheduled_date": friday_date
            })

        db = self.engine.load_db()
        self.assertEqual(len(db["scripts"]), 6)
        assigned_slots = {s["scheduled_slot"] for s in db["scripts"]}
        self.assertEqual(assigned_slots, {1, 2, 3, 4, 5, 6}, "All 6 daily slots must be uniquely assigned!")

        slot5_script = next(s for s in db["scripts"] if s["scheduled_slot"] == 5)
        self.assertEqual(slot5_script["recommended_time"], "21:00")
        self.assertEqual(slot5_script["online_followers"], 21970)
        self.assertIn("جمعه", slot5_script["weekday_fa"])

    def test_02_publish_appends_sequentially_to_both_history_files(self):
        """Verify publishing scripts assigns #234, #235 sequentially and updates both history files cleanly."""
        s1 = self.engine.add_script({
            "id": "pub-test-1",
            "title": "اسکریپت اول تست انتشار",
            "archetype": "آرکتایپ ۱",
            "content": "هوک اختصاصی تست ۲۳۴\nمیانه متن\nپایان اختصاصی ۲۳۴",
            "caption": "کپشن تست ۲۳۴"
        })
        s2 = self.engine.add_script({
            "id": "pub-test-2",
            "title": "اسکریپت دوم تست انتشار",
            "archetype": "آرکتایپ ۳",
            "content": "هوک اختصاصی تست ۲۳۵\nمیانه متن\nپایان اختصاصی ۲۳۵",
            "caption": "کپشن تست ۲۳۵"
        })

        with open(self.root_hist, "r", encoding="utf-8") as f:
            base_hist = f.read()
        expected_first = self.engine._get_next_history_number(self.engine.load_db(), base_hist)
        expected_second = expected_first + 1

        res1 = self.engine.publish_script(s1["id"])
        self.assertTrue(res1["published"])
        self.assertEqual(res1["history_reel_number"], expected_first)

        res2 = self.engine.publish_script(s2["id"])
        self.assertTrue(res2["published"])
        self.assertEqual(res2["history_reel_number"], expected_second)

        # Verify both root and skill history markdown files contain expected_first and expected_second
        for hist_path in (self.root_hist, self.skill_hist):
            with open(hist_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn(f"| **#{expected_first}** |", content)
            self.assertIn(f"| **#{expected_second}** |", content)
            self.assertIn(f"### Reel #{expected_first} (✅ [PUBLISHED])", content)
            self.assertIn(f"### Reel #{expected_second} (✅ [PUBLISHED])", content)
            self.assertIn("هوک اختصاصی تست ۲۳۴", content)
            self.assertIn("هوک اختصاصی تست ۲۳۵", content)
            # Ensure original Reel #1 and Reel #233 are untouched
            self.assertIn("### Reel #1 (🔥 [VIRAL])", content)
            self.assertIn("### Reel #233 (❌ [FLOP])", content)

    def test_03_idempotency_repeated_publish_never_duplicates(self):
        """Verify clicking publish multiple times on the same script never creates duplicate entries in history."""
        s1 = self.engine.add_script({
            "id": "idem-test-1",
            "title": "تست عدم تکرار",
            "content": "هوک یکتای تست ایدمپوتنسی\nپایان یکتا",
            "caption": "کپشن یکتا"
        })

        with open(self.root_hist, "r", encoding="utf-8") as f:
            expected_num = self.engine._get_next_history_number(self.engine.load_db(), f.read())

        for _ in range(5):
            res = self.engine.publish_script(s1["id"])
            self.assertEqual(res["history_reel_number"], expected_num)

        with open(self.root_hist, "r", encoding="utf-8") as f:
            text = f.read()

        # Marker should appear exactly 3 times (once in Sec 1 table, once in Sec 2 table, once in Sec 3 header)
        marker = "<!-- SCRIPT_ID:idem-test-1 -->"
        self.assertEqual(text.count(marker), 3)
        self.assertEqual(text.count(f"### Reel #{expected_num} (✅ [PUBLISHED])"), 1)

    def test_04_unpublish_cleanly_removes_entry_without_corrupting_233_reels(self):
        """Verify unchecking publish removes #234 from both history files and preserves all 233 base reels."""
        s1 = self.engine.add_script({
            "id": "unpub-test-1",
            "title": "تست لغو انتشار منحصربه‌فرد",
            "content": "یک متن کاملاً مجزا و آزمایشی برای بررسی حذف امن و لغو انتشار بدون تداخل در سیستم\nپایان تست منحصربه‌فرد",
            "caption": "کپشن تستی مجزا"
        })

        self.engine.publish_script(s1["id"])
        with open(self.root_hist, "r", encoding="utf-8") as f:
            after_pub = f.read()
        self.assertIn("<!-- SCRIPT_ID:unpub-test-1 -->", after_pub)

        # Now unpublish
        res_unpub = self.engine.unpublish_script(s1["id"])
        self.assertFalse(res_unpub["published"])
        self.assertIsNone(res_unpub["history_reel_number"])

        for hist_path in (self.root_hist, self.skill_hist):
            with open(hist_path, "r", encoding="utf-8") as f:
                after_unpub = f.read()
            self.assertNotIn("<!-- SCRIPT_ID:unpub-test-1 -->", after_unpub)
            self.assertNotIn("هوک موقت برای حذف", after_unpub)
            self.assertIn("### Reel #1 (🔥 [VIRAL])", after_unpub)
            self.assertIn("### Reel #233 (❌ [FLOP])", after_unpub)

    def test_05_real_db_has_6_scripts_across_all_6_daily_slots(self):
        """Verify the production data/scripts-db.json is valid and pre-populated with 6 ready scripts."""
        prod_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "scripts-db.json")
        with open(prod_db_path, "r", encoding="utf-8") as f:
            prod_db = json.load(f)
        self.assertEqual(prod_db["meta"]["daily_goal"], 6)
        self.assertGreaterEqual(len(prod_db["scripts"]), 6)
        slots = {s["scheduled_slot"] for s in prod_db["scripts"]}
        self.assertEqual(slots, {1, 2, 3, 4, 5, 6})

    def test_06_batch_import_4_days_24_reels_and_source_metadata(self):
        """Test importing 4 batches of 6 viral reels (24 reels) across 4 days + source metadata persistence."""
        archetypes_cycle = [
            "آرکتایپ ۵: مانیفست رفتاربینی و عدالت خدا",
            "آرکتایپ ۶: مینی‌روایت دیالوگی و برش زندگی",
            "آرکتایپ ۴: گلایه بی‌دفاع در رابطه",
            "آرکتایپ ۳: تقدیم‌نامه به آدم امن و ریشه‌دار",
            "آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب",
            "آرکتایپ ۲: خداحافظی باوقار و پذیرش پایان",
        ]
        items = []
        for idx in range(24):
            arch = archetypes_cycle[idx % 6]
            items.append({
                "title": f"ریلز شکارشده وایرال شماره {idx + 1}",
                "archetype": arch,
                "goal": "جذب فالوور و شیر بالا",
                "score": 97,
                "is_viral_hunted": True,
                "source_url": f"https://www.instagram.com/reel/VIRAL{idx + 1:02d}/",
                "source_page": f"@viral_mother_page_{(idx % 4) + 1}",
                "source_views": f"{450 + idx * 25}K بازدید",
                "extracted_raw_text": f"سطر اول متن خام ویدیو {idx + 1}\nسطر دوم متن خام استخراج‌شده با دقت صددرصد",
                "extra_notes": "پس‌زمینه مشکی، فونت سفید، موزیک پیانو",
                "content": f"هوک بومی‌سازی‌شده ریلز {idx + 1}\nپله دوم روایت\nضربه نهایی باوقار {idx + 1}",
                "caption": f"کپشن مکمل ریلز {idx + 1}؟",
            })

        res = self.engine.batch_import_and_schedule(items, start_date="2026-10-01")
        self.assertEqual(len(res), 24)

        expected_dates = ["2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04"]
        db = self.engine.load_db()
        for d_str in expected_dates:
            day_list = [s for s in db["scripts"] if s["scheduled_date"] == d_str]
            self.assertEqual(len(day_list), 6, f"Expected 6 reels on {d_str}")
            slots_for_day = {s["scheduled_slot"] for s in day_list}
            self.assertEqual(slots_for_day, {1, 2, 3, 4, 5, 6}, f"All 6 slots must be filled on {d_str}")
            # Check that peak slot 6 (23:45) got Archetype 1 or 2
            slot6_reel = [s for s in day_list if s["scheduled_slot"] == 6][0]
            self.assertTrue(
                "آرکتایپ ۱" in slot6_reel["archetype"] or "آرکتایپ ۲" in slot6_reel["archetype"],
                f"Slot 6 should have Archetype 1 or 2, got {slot6_reel['archetype']}"
            )
            # Check source metadata fields
            self.assertTrue(slot6_reel["is_viral_hunted"])
            self.assertTrue(slot6_reel["source_url"].startswith("https://www.instagram.com/reel/"))
            self.assertIn("بازدید", slot6_reel["source_views"])
            self.assertIn("متن خام", slot6_reel["extracted_raw_text"])

        # Also test updating source metadata via update_script_metadata
        first_id = db["scripts"][0]["id"]
        upd = self.engine.update_script_metadata(first_id, {
            "source_views": "1.2M بازدید",
            "extra_notes": "بروزرسانی یادداشت تست",
        })
        self.assertEqual(upd["source_views"], "1.2M بازدید")
        self.assertEqual(upd["extra_notes"], "بروزرسانی یادداشت تست")

    def test_07_persona_fit_audit_and_post_mortem_score_calibration(self):
        """Test 5-pillar Viral Probability Score breakdown, Persona Fit Reason, and Post-Mortem analysis when high score underperforms."""
        sc = self.engine.add_script({
            "title": "تست نمره احتمال وایرال شدن و کالبدشکافی",
            "archetype": "آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب",
            "content": "متن تستی شبیه‌سازی کالبدشکافی بدون همپوشانی با بانک کلمات\nپرده دوم تستی\nضربه نهایی تستی",
            "caption": "تو هم همینطوری؟",
            "scheduled_date": "2026-10-05",
            "scheduled_slot": 2,
            "is_viral_hunted": True,
            "source_url": "https://www.instagram.com/reel/TEST99/",
            "source_views": "750K بازدید",
        })
        self.assertIn("score_breakdown", sc)
        self.assertEqual(sc["score_breakdown"]["persona_fit"], 20)
        self.assertIn("تطابق ۱۰۰٪ با پرسونای", sc["persona_fit_reason"])

        # Simulate recording underperformance despite high score
        calibrated = self.engine.update_script_metadata(sc["id"], {
            "actual_views": "11,200 بازدید",
            "actual_result": "UNDERPERFORMED",
        })
        self.assertEqual(calibrated["actual_result"], "UNDERPERFORMED")
        self.assertIn("کالبدشکافی اختلاف نمره بالا با بازخورد واقعی", calibrated["post_mortem_analysis"])

    def test_08_automatic_history_anti_duplication_blocks_existing_233_reels(self):
        """Verify that check_duplicate_against_history automatically blocks reels already in published-content-history.md."""
        # Reel #73 from published-content-history.md
        dup_text_73 = (
            "افرادی که عمیقاً یکدیگر را دوست دارند، هنگام دوری از هم با یکدیگر دعوا می‌کنند "
            "و حس می‌کنند از هم ناراحتند، اما موقعی که کنار هم هستند آن احساسات از بین می‌رود "
            "و انگار هیچ اتفاقی بین آن‌ها رخ نداده. به این احساس عشق و وابستگی واقعی می‌گویند که از بین نمی‌رود."
        )
        check_73 = self.engine.check_duplicate_against_history(dup_text_73, dup_text_73)
        self.assertTrue(check_73["is_duplicate"])
        self.assertTrue(check_73["duplicate_of_reel"] in ["Reel #73", "DcB517Qqp0z"] or len(check_73["duplicate_of_reel"]) > 0)
        self.assertGreaterEqual(check_73["similarity_score"], 85.0)

        # Attempting to add it via add_script must raise ValueError(DUPLICATE_REEL_BLOCKED)
        with self.assertRaises(ValueError) as ctx:
            self.engine.add_script({
                "title": "تست پست تکراری شماره ۷۳",
                "archetype": "آرکتایپ ۳: تقدیم‌نامه به آدم امن و ریشه‌دار",
                "content": dup_text_73,
                "extracted_raw_text": dup_text_73,
            })
        self.assertIn("DUPLICATE_REEL_BLOCKED", str(ctx.exception))

    def test_09_cover_custom_styling_and_line_break_support(self):
        """Verify build_cover_html supports custom line breaks, font size, line height, top offset, and colors."""
        import scripts.post_maker as post_maker

        # Test multi-line custom break with \n
        custom_hook = "خط اول هوک کاور\nخط دوم هوک با ریتم دلخواه"
        html = post_maker.build_cover_html(
            custom_hook,
            theme="dark",
            custom_style={
                "cover_font_size": 115,
                "cover_line_height": 185,
                "cover_top_offset": 520,
                "cover_color": "gold",
                "cover_is_bold": True
            }
        )
        self.assertIn("<div>خط اول هوک کاور</div>", html)
        self.assertIn("<div>خط دوم هوک با ریتم دلخواه</div>", html)
        self.assertIn("115px", html)
        self.assertIn("185px", html)
        self.assertIn("520px", html)
        self.assertIn("#F4C466", html)
        self.assertIn("font-weight: bold", html)
        self.assertIn("IRTitr", html)

        # Test light theme default styling
        html_light = post_maker.build_cover_html(
            "هوک بدون شکست دستی سطر برای بررسی شکست خودکار کلمات",
            theme="light"
        )
        self.assertIn("#171717", html_light)
        self.assertIn("90px", html_light)
        self.assertIn("145px", html_light)
        self.assertIn("568px", html_light)

    def test_10_update_script_metadata_persists_hook(self):
        """Verify engine.update_script_metadata cleanly persists edited hook to the database."""
        sc = self.engine.add_script({
            "title": "اسکریپت تست تغییر هوک",
            "content": "متن تستی برای ویرایش هوک\nپایان متن",
            "caption": "کپشن تستی",
            "hook": "هوک قدیمی اولیه",
            "allow_duplicate": True
        })
        self.assertEqual(sc["hook"], "هوک قدیمی اولیه")

        updated = self.engine.update_script_metadata(sc["id"], {
            "hook": "هوک تازه ویرایش‌شده روی کاور\nبا دو خط اختصاصی"
        })
        self.assertEqual(updated["hook"], "هوک تازه ویرایش‌شده روی کاور\nبا دو خط اختصاصی")

        # Verify DB file on disk actually contains the updated hook
        db = self.engine.load_db()
        matched = next(s for s in db["scripts"] if s["id"] == sc["id"])
        self.assertEqual(matched["hook"], "هوک تازه ویرایش‌شده روی کاور\nبا دو خط اختصاصی")

    def test_11_render_preview_png_bytes_for_cover(self):
        """Verify render_preview_png_bytes generates a valid 1080x1920 PNG for cover type with custom style."""
        import scripts.post_maker as post_maker
        png_bytes = post_maker.render_preview_png_bytes(
            slot=1,
            item_type="cover",
            custom_hook="تیتر جذاب کاور\nسطر دوم تست",
            custom_style={
                "cover_font_size": 100,
                "cover_line_height": 165,
                "cover_color": "cream"
            }
        )
        self.assertGreater(len(png_bytes), 1000)
        self.assertEqual(png_bytes[:8], b"\x89PNG\r\n\x1a\n")

    def test_12_extract_audio_from_local_video(self):
        """Verify extract_audio_from_local_video extracts MP3 audio track and metadata."""
        from media_downloader import extract_audio_from_local_video, list_system_downloaded_reels
        reels = list_system_downloaded_reels()
        self.assertIsInstance(reels, list)
        if reels:
            v_path = reels[0]["path"]
            res = extract_audio_from_local_video(v_path, scheduled_date="2026-10-19", scheduled_slot=98)
            self.assertTrue(res.get("ok"))
            self.assertTrue(os.path.exists(res.get("audio_path")))
            self.assertGreater(res.get("duration_seconds", 0), 0)
            self.assertEqual(res.get("track", {}).get("is_source_track"), True)
            if os.path.exists(res["audio_path"]):
                os.remove(res["audio_path"])
            if res.get("frame_path") and os.path.exists(res["frame_path"]):
                os.remove(res["frame_path"])


if __name__ == "__main__":
    unittest.main(verbosity=2)



