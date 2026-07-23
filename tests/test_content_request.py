"""Tests for Content Agent V1 request parsing."""

import unittest

from utils.content_request import SUPPORTED_PLATFORMS, build_content_brief


class ContentRequestTests(unittest.TestCase):
    def test_defaults_to_all_short_video_platforms(self) -> None:
        brief = build_content_brief("AI ช่วยช่างทองได้อย่างไร")
        self.assertEqual(brief.platforms, SUPPORTED_PLATFORMS)
        self.assertEqual(brief.duration_seconds, 45)
        self.assertTrue(brief.approval_required)

    def test_detects_requested_platform_and_duration(self) -> None:
        brief = build_content_brief("คลิป 60 วินาที สำหรับ TikTok เรื่องการตรวจเตย")
        self.assertEqual(brief.platforms, ("tiktok",))
        self.assertEqual(brief.duration_seconds, 60)

    def test_detects_multiple_platforms(self) -> None:
        brief = build_content_brief("ทำคลิปสำหรับ YouTube Shorts และ Facebook Reels")
        self.assertEqual(brief.platforms, ("youtube_shorts", "facebook_reels"))

    def test_rejects_empty_topic(self) -> None:
        with self.assertRaises(ValueError):
            build_content_brief("   ")


if __name__ == "__main__":
    unittest.main()
