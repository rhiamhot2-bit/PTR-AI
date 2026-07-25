"""Tests for Content Agent V2 request parsing."""

import unittest

from utils.content_request import SUPPORTED_PLATFORMS, build_content_brief


class ContentRequestTests(unittest.TestCase):
    def test_defaults_to_all_short_video_platforms(self) -> None:
        brief = build_content_brief("AI ช่วยช่างทองได้อย่างไร")
        self.assertEqual(brief.platforms, SUPPORTED_PLATFORMS)
        self.assertEqual(brief.duration_seconds, 45)
        self.assertEqual(brief.output_format, "content_pack_v2")
        self.assertEqual(brief.presenter_mode, "thiam_plus_ptr_ai")
        self.assertTrue(brief.approval_required)
        self.assertFalse(brief.auto_publish)

    def test_detects_requested_platform_duration_and_style(self) -> None:
        brief = build_content_brief("คลิปสอน 60 วินาที สำหรับ TikTok เรื่องการตรวจเตย")
        self.assertEqual(brief.platforms, ("tiktok",))
        self.assertEqual(brief.duration_seconds, 60)
        self.assertIn("tutorial", brief.styles)

    def test_detects_multiple_platforms(self) -> None:
        brief = build_content_brief("ทำคลิปสำหรับ YouTube Shorts และ Facebook Reels")
        self.assertEqual(brief.platforms, ("youtube_shorts", "facebook_reels"))

    def test_defaults_to_jewelry_ai_education_styles(self) -> None:
        brief = build_content_brief("ระบบช่วยตรวจงาน")
        self.assertEqual(brief.styles, ("education", "jewelry", "ai"))
        self.assertEqual(brief.knowledge_mode, "jewelry_expert")
        self.assertEqual(brief.spoken_language, "thai")

    def test_supports_eight_second_veo_scene(self) -> None:
        brief = build_content_brief("คลิป 8 วินาที เรื่องแหวนมรกต")
        self.assertEqual(brief.duration_seconds, 8)

    def test_rejects_empty_topic(self) -> None:
        with self.assertRaises(ValueError):
            build_content_brief("   ")


if __name__ == "__main__":
    unittest.main()
