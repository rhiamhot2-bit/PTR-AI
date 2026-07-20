import tempfile
import unittest
from pathlib import Path

from utils.seat_thickness_correction_trial_generator import (
    SOURCE_NAME,
    TRIAL_NAME,
    prepare_seat_thickness_correction_trial,
    save_seat_thickness_correction_trial,
)


class SeatThicknessCorrectionTrialTests(unittest.TestCase):
    def test_generated_script_is_copy_only_and_uses_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "Job_Profiles").mkdir()
            (root / "Job_Profiles" / "current.json").write_text('{"minimum_member_mm": 0.8}', encoding="utf-8")
            path, report, script = prepare_seat_thickness_correction_trial(root)
            compile(script, str(path), "exec")
            self.assertIn(SOURCE_NAME, script)
            self.assertIn(TRIAL_NAME, script)
            self.assertIn("TARGET_MM = 0.8", script)
            self.assertIn("DuplicateBrep", script)
            self.assertIn("BOOLEAN | NOT EXECUTED", script)
            self.assertNotIn("DeleteObject(", script)
            self.assertNotIn("BooleanUnion(", script)
            save_seat_thickness_correction_trial(path, script)
            self.assertTrue(path.exists())
            self.assertIn("Seat_Thickness_Correction_Trials", str(report))

    def test_default_target_is_safe(self):
        with tempfile.TemporaryDirectory() as folder:
            _, _, script = prepare_seat_thickness_correction_trial(Path(folder))
            self.assertIn("TARGET_MM = 0.8", script)


if __name__ == "__main__":
    unittest.main()
