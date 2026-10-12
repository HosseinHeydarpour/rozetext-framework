import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import PublisherEngine, STORIES_DB_PATH

class TestStoryPublisher(unittest.TestCase):
    def setUp(self):
        self.engine = PublisherEngine()

    def test_01_load_stories_db(self):
        db = self.engine.load_stories_db()
        self.assertIn("stories", db)
        self.assertGreaterEqual(len(db["stories"]), 7, "Must contain at least 7 days of story scenarios!")
        
        # Check weekdays coverage
        weekdays = {s.get("weekday") for s in db["stories"]}
        expected_weekdays = {"شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"}
        self.assertTrue(expected_weekdays.issubset(weekdays), f"All 7 weekdays must be covered! Got: {weekdays}")

    def test_02_story_structure_completeness(self):
        db = self.engine.load_stories_db()
        for s in db["stories"]:
            self.assertIn("id", s)
            self.assertIn("date", s)
            self.assertIn("story_sequence", s)
            self.assertGreaterEqual(len(s["story_sequence"]), 2, "Each day must have at least 2 story steps!")
            
            # Step 1 must have interactive sticker and visual aesthetic
            step1 = s["story_sequence"][0]
            self.assertIn("sticker", step1)
            self.assertIn("visual_aesthetic", step1)
            self.assertIn("text_content", step1)
            
            # AI image generation prompt for background
            va = step1["visual_aesthetic"]
            self.assertIn("ai_image_prompt", va, f"Story {s['id']} must have ai_image_prompt in visual_aesthetic!")
            self.assertTrue(len(va["ai_image_prompt"]) > 20, f"AI image prompt must be descriptive!")
            self.assertIn("9:16", va["ai_image_prompt"], "Prompt must specify 9:16 aspect ratio!")

            # AI music generation prompt for Suno & Gemini
            self.assertIn("ai_music_prompt", va, f"Story {s['id']} must have ai_music_prompt in visual_aesthetic!")
            mp = va["ai_music_prompt"]
            self.assertIn("suno_style_tags", mp)
            self.assertIn("suno_lyrics_structure", mp)
            self.assertIn("gemini_detailed_prompt", mp)
            self.assertIn("Instrumental", mp["suno_lyrics_structure"], "Music prompt must be 100% instrumental!")
            self.assertTrue(len(mp["gemini_detailed_prompt"]) > 40, "Gemini music prompt must be detailed!")

            # Pinned comment and monetization guide
            self.assertIn("pinned_comment", s)
            self.assertIn("monetization_guide", s)

    def test_03_toggle_publish_story(self):
        db = self.engine.load_stories_db()
        first_story = db["stories"][0]
        sid = first_story["id"]
        initial_status = first_story.get("published", False)

        # Toggle once
        toggled = self.engine.toggle_publish_story(sid)
        self.assertEqual(toggled["published"], not initial_status)
        if toggled["published"]:
            self.assertIsNotNone(toggled["published_at"])

        # Toggle back to restore original state
        restored = self.engine.toggle_publish_story(sid)
        self.assertEqual(restored["published"], initial_status)

if __name__ == "__main__":
    unittest.main()
