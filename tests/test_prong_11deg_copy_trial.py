"""Tests for Prong 11 Degree Copy Trial."""
import tempfile,unittest
from datetime import datetime
from pathlib import Path
from utils.prong_11deg_copy_trial_generator import build_prong_11deg_copy_trial_script,prepare_prong_11deg_copy_trial,save_prong_11deg_copy_trial,additional_tilt_deg
class Prong11TrialTests(unittest.TestCase):
    def test_adjustment(self):
        self.assertEqual(additional_tilt_deg(6.178),4.822)
        self.assertEqual(additional_tilt_deg(11.0),0.0)
    def test_script(self):
        script=build_prong_11deg_copy_trial_script(Path("report.json"))
        compile(script,"prong11.py","exec")
        self.assertIn("rs.CopyObject",script)
        self.assertIn("rs.RotateObject(copy_id",script)
        self.assertIn("center.X-seat_center.X",script)
        self.assertIn('"direction_rule":"OUTWARD_FROM_SEAT_CENTER"',script)
        self.assertIn("VectorAngle(current_axis,desired_axis)",script)
        self.assertIn("rs.MoveObject(copy_id",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.Boolean",script)
        self.assertIn("ORIGINAL GEOMETRY MODIFIED | NO",script)
    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_prong_11deg_copy_trial(Path(folder),datetime(2026,7,18,19,45,0))
            save_prong_11deg_copy_trial(path,script)
            self.assertTrue(path.exists())
if __name__=="__main__":unittest.main()
