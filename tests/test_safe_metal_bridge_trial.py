"""Tests for Safe Metal Bridge Trial."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.safe_metal_bridge_trial_generator import (
    build_safe_metal_bridge_trial_script,
    is_trial_gap,
    prepare_safe_metal_bridge_trial,
    save_safe_metal_bridge_trial,
    trial_span_mm,
)


class SafeMetalBridgeTrialTests(unittest.TestCase):
    def test_trial_gap_limits(self):
        self.assertFalse(is_trial_gap(0.05))
        self.assertTrue(is_trial_gap(0.695))
        self.assertTrue(is_trial_gap(1.50))
        self.assertFalse(is_trial_gap(1.501))

    def test_span_includes_overlap_at_both_ends(self):
        self.assertEqual(trial_span_mm(0.695), 0.995)

    def test_generated_script_compiles_and_protects_originals(self):
        script = build_safe_metal_bridge_trial_script(Path("bridge_trial.json"))
        compile(script, "safe_metal_bridge_trial.py", "exec")
        self.assertIn("rs.AddCylinder", script)
        self.assertIn("PTR_METAL_BRIDGE_TRIAL", script)
        for forbidden in ("rs.Delete", "rs.Move", "rs.Boolean", "rs.Command", "rs.Save"):
            self.assertNotIn(forbidden, script)
        self.assertIn("ORIGINAL GEOMETRY MODIFIED | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_safe_metal_bridge_trial(
                root, datetime(2026, 7, 18, 17, 30, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Metal_Bridge_Trials")
            save_safe_metal_bridge_trial(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
