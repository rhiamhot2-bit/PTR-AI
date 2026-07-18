"""Tests for Prong Length Correction Trial."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_length_correction_trial_generator import (
    build_prong_length_correction_trial_script,
    prepare_prong_length_correction_trial,
    required_addition,
    save_prong_length_correction_trial,
)

class ProngLengthCorrectionTrialTests(unittest.TestCase):
    def test_required_addition(self):
        self.assertEqual(required_addition(0.699),0.101)
        self.assertEqual(required_addition(0.702),0.098)
        self.assertEqual(required_addition(0.9),0.0)

    def test_non_destructive_script(self):
        script=build_prong_length_correction_trial_script(Path("report.json"))
        compile(script,"trial.py","exec")
        self.assertIn("DuplicateBrep()",script)
        self.assertIn("Transform.Scale(plane, 1.0, 1.0, factor)",script)
        self.assertIn("PTR_MIN_SEAT_ENGAGEMENT_RATIO",script)
        self.assertNotIn("rs.Command",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("CreateBooleanUnion",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_prong_length_correction_trial(
                Path(folder),datetime(2026,7,19,0,30,0)
            )
            save_prong_length_correction_trial(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Prong_Length_Correction_Trials",str(report))

if __name__=="__main__":
    unittest.main()
