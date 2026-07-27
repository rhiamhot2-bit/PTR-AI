"""Tests for Content Agent V2 Integration request parsing."""

import unittest

from utils.content_request import SUPPORTED_PLATFORMS, build_content_brief


class ContentRequestTests(unittest.TestCase):
    def test_defaults_are_review_first(self) -> None:
        brief = build_content_brief("AI ช่วยช่างทองได้อย่างไร")
        self.assertEqual(brief.platforms, SUPPORTED_PLATFORMS)
        self.assertEqual(brief.duration_seconds, 45)
        self.assertEqual(brief.output_format, "ptr_content_contract_v1")
        self.assertEqual(brief.status, "needs_review")
        self.assertTrue(brief.human_approval_required)
        self.assertFalse(brief.auto_publish)

    def test_detects_platform_duration_and_style(self) -> None:
        brief = build_content_brief(
            "คลิปสอน 60 วินาที สำหรับ TikTok เรื่องการตรวจเตย"
        )
        self.assertEqual(brief.platforms, ("tiktok",))
        self.assertEqual(brief.duration_seconds, 60)
        self.assertIn("tutorial", brief.styles)
        self.assertEqual(brief.mode, "jewelry_expert")

    def test_detects_asset_reuse_placeholders(self) -> None:
        brief = build_content_brief("นำคลิปเก่าขับรถมาทำวิดีโอใหม่")
        self.assertEqual(brief.mode, "asset_reuse")
        self.assertEqual(brief.asset_search_query, brief.topic)
        self.assertEqual(brief.audio_permission, "unknown")
        self.assertEqual(brief.usage_rights, "unknown")

    def test_detects_access_tier(self) -> None:
        self.assertEqual(
            build_content_brief("ทำคอนเทนต์พรีเมียมขายลูกค้า").access_tier,
            "professional",
        )
        self.assertEqual(
            build_content_brief("คู่มือภายในทีมงาน").access_tier,
            "internal",
        )

    def test_rejects_empty_topic(self) -> None:
        with self.assertRaises(ValueError):
            build_content_brief("   ")


if __name__ == "__main__":
    unittest.main()
