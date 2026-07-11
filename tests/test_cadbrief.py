import unittest

from utils.cadbrief import parse_cad_brief


class CadBriefParserTests(unittest.TestCase):
    def test_complete_thai_ring_brief_is_ready(self) -> None:
        brief = parse_cad_brief(
            "แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. ฝังหนามเตย 4 เตย"
        )
        self.assertEqual(brief["jewelry_type"], "ring")
        self.assertEqual(brief["ring_size"], 52)
        self.assertEqual(brief["metal"], "18K gold")
        self.assertEqual(brief["center_stone"]["type"], "emerald")
        self.assertEqual(brief["center_stone"]["shape"], "oval")
        self.assertEqual(brief["center_stone"]["length_mm"], 8)
        self.assertEqual(brief["center_stone"]["width_mm"], 6)
        self.assertEqual(brief["setting"]["type"], "prong")
        self.assertEqual(brief["setting"]["prong_count"], 4)
        self.assertEqual(brief["status"], "ready_for_cad")
        self.assertEqual(brief["missing_fields"], [])

    def test_incomplete_brief_reports_missing_fields(self) -> None:
        brief = parse_cad_brief("แหวนทอง 18K มรกต")
        self.assertEqual(brief["status"], "needs_information")
        self.assertIn("ไซซ์แหวน", brief["missing_fields"])
        self.assertIn("รูปทรงพลอย", brief["missing_fields"])
        self.assertIn("ขนาดพลอย", brief["missing_fields"])
        self.assertIn("รูปแบบการฝัง", brief["missing_fields"])


if __name__ == "__main__":
    unittest.main()
