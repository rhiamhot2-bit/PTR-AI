import unittest

from utils.cad_rules import validate_cad_request


BASE = (
    "แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย "
    "ก้านกว้าง 2.5 มม. ก้านหนา 1.8 มม. "
)


class CadRulesTests(unittest.TestCase):
    def test_safe_values_are_ready_for_rhino_review(self) -> None:
        report = validate_cad_request(
            BASE
            + "หนามเตยหนา 0.7 มม. ระยะเผื่อฝัง 0.1 มม. หัวแหวนสูง 6.5 มม."
        )
        self.assertEqual(report["overall_status"], "ready_for_rhino")
        self.assertTrue(all(item["status"] == "pass" for item in report["checks"]))

    def test_missing_values_need_information(self) -> None:
        report = validate_cad_request(BASE)
        self.assertEqual(report["overall_status"], "needs_information")
        missing = {item["field"] for item in report["checks"] if item["status"] == "missing"}
        self.assertIn("prong_diameter_mm", missing)
        self.assertIn("seat_clearance_mm", missing)
        self.assertIn("head_height_mm", missing)

    def test_unsafe_values_block_script_generation(self) -> None:
        report = validate_cad_request(
            BASE
            + "หนามเตยหนา 0.4 มม. ระยะเผื่อฝัง 0.3 มม. หัวแหวนสูง 8 มม."
        )
        self.assertEqual(report["overall_status"], "blocked")
        failed = {item["field"] for item in report["checks"] if item["status"] == "fail"}
        self.assertIn("prong_diameter_mm", failed)
        self.assertIn("seat_clearance_mm", failed)


if __name__ == "__main__":
    unittest.main()
