import tempfile
import unittest
from pathlib import Path

from utils.seat_thickness_correction_validator_generator import (
    TRIAL_NAME,
    prepare_seat_thickness_correction_validator,
    save_seat_thickness_correction_validator,
)


class SeatThicknessCorrectionValidatorTests(unittest.TestCase):
    def test_generated_validator_is_report_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, report, script = prepare_seat_thickness_correction_validator(root)
            compile(script, str(path), "exec")
            self.assertIn(TRIAL_NAME, script)
            self.assertIn("IsSolid", script)
            self.assertIn("DuplicateNakedEdgeCurves", script)
            self.assertIn("GEOMETRY MODIFIED | NO", script)
            self.assertNotIn("Transform(", script)
            self.assertNotIn("DeleteObject(", script)
            self.assertNotIn("BooleanUnion(", script)
            save_seat_thickness_correction_validator(path, script)
            self.assertTrue(path.exists())
            self.assertIn("Seat_Thickness_Correction_Validation", str(report))

    def test_profile_target_is_embedded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "Job_Profiles").mkdir()
            (root / "Job_Profiles" / "current.json").write_text('{"minimum_member_mm": 0.95}', encoding="utf-8")
            _, _, script = prepare_seat_thickness_correction_validator(root)
            self.assertIn("TARGET_MM = 0.95", script)


if __name__ == "__main__":
    unittest.main()
