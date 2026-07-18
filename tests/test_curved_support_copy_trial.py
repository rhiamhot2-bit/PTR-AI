"""Tests for Curved Support Copy Trial."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.curved_support_copy_trial_generator import (
    build_curved_support_copy_trial_script,
    prepare_curved_support_copy_trial,
    save_curved_support_copy_trial,
    trial_status,
)

class CurvedSupportTrialTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(trial_status(2,2),"CURVED_SUPPORT_TRIAL_CREATED")
        self.assertEqual(trial_status(1,1),"CURVED_SUPPORT_TRIAL_BLOCKED")
        self.assertEqual(trial_status(2,1),"CURVED_SUPPORT_TRIAL_INCOMPLETE")

    def test_copy_only_script(self):
        script=build_curved_support_copy_trial_script(Path("report.json"))
        compile(script,"curved_support.py","exec")
        self.assertIn("Curve.CreateInterpolatedCurve",script)
        self.assertIn("Brep.CreatePipe",script)
        self.assertIn("CONTACT_OVERLAP_MM=0.20",script)
        self.assertIn("STONE_SEAT_100_PERCENT",script)
        self.assertIn("RING_BAND_100_PERCENT",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)
        self.assertNotIn("CreateBooleanUnion",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_curved_support_copy_trial(
                Path(folder),datetime(2026,7,18,22,0,0)
            )
            save_curved_support_copy_trial(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Curved_Support_Trials",str(report))

if __name__=="__main__":
    unittest.main()
