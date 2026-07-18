"""Tests for the Prong 11 Degree Trial Validator."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_11deg_trial_validator_generator import (
    build_prong_11deg_trial_validator_script,
    classify_prong_trial,
    prepare_prong_11deg_trial_validator,
    save_prong_11deg_trial_validator,
)

class Prong11ValidatorTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_prong_trial(True, True, 11.0, .25, False), "READY_FOR_REPOSITION_REHEARSAL")
        self.assertEqual(classify_prong_trial(True, False, 11.0, .25, False), "TILTS_INWARD")
        self.assertEqual(classify_prong_trial(True, True, 10.0, .25, False), "TILT_OUT_OF_TOLERANCE")
        self.assertEqual(classify_prong_trial(True, True, 11.0, .24, False), "ENGAGEMENT_TOO_SHALLOW")
        self.assertEqual(classify_prong_trial(True, True, 11.0, .25, True), "STONE_LOADING_COLLISION")

    def test_report_only_script(self):
        script = build_prong_11deg_trial_validator_script(Path("report.json"))
        compile(script, "validator.py", "exec")
        self.assertIn("outward_dot > 0.0", script)
        self.assertIn("MIN_ENGAGEMENT_RATIO = 0.25", script)
        self.assertIn("MAX_SYMMETRY_SPREAD_DEG = 0.50", script)
        self.assertIn("Brep.CreateBooleanIntersection", script)
        self.assertIn("IN_MEMORY_BOOLEAN_INTERSECTION_RADIAL_DEPTH", script)
        self.assertIn("DOCUMENT BOOLEAN | NOT EXECUTED", script)
        self.assertNotIn("sc.doc.Objects.AddBrep", script)
        self.assertNotIn("rs.MoveObject", script)
        self.assertNotIn("rs.RotateObject", script)
        self.assertNotIn("rs.Delete", script)
        self.assertNotIn("CreateBooleanUnion", script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path, report, script = prepare_prong_11deg_trial_validator(
                Path(folder), datetime(2026, 7, 18, 21, 10, 0)
            )
            save_prong_11deg_trial_validator(path, script)
            self.assertTrue(path.exists())
            self.assertIn("Prong_11Deg_Validation", str(report))

if __name__ == "__main__":
    unittest.main()
