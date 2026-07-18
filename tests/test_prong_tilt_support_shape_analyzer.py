"""Tests for Prong Tilt and Support Shape Analyzer."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_tilt_support_shape_analyzer_generator import (
    build_prong_tilt_support_shape_analyzer_script,
    prepare_prong_tilt_support_shape_analyzer,
    save_prong_tilt_support_shape_analyzer,
    support_shape,
    tilt_adjustment_deg,
)
class TiltShapeTests(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(tilt_adjustment_deg(8.0), 3.0)
        self.assertEqual(tilt_adjustment_deg(13.0), -2.0)
        self.assertEqual(support_shape(0.08), "STRAIGHT")
        self.assertEqual(support_shape(0.081), "CURVED")
    def test_script_compiles_and_is_report_only(self):
        script = build_prong_tilt_support_shape_analyzer_script(Path("report.json"))
        compile(script, "tilt_shape.py", "exec")
        self.assertIn("principal_axis", script)
        self.assertIn("TARGET_PRONG_TILT_DEG = 11.0", script)
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Rotate", "rs.Boolean"):
            self.assertNotIn(forbidden, script)
    def test_prepare_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            path, report, script=prepare_prong_tilt_support_shape_analyzer(root,datetime(2026,7,18,19,30,0))
            save_prong_tilt_support_shape_analyzer(path,script)
            self.assertTrue(path.exists())
if __name__=="__main__":
    unittest.main()
