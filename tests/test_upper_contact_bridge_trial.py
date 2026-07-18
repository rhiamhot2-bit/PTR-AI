"""Tests for Upper Contact Bridge Trial."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.upper_contact_bridge_trial_generator import (
    build_upper_contact_bridge_trial_script,
    prepare_upper_contact_bridge_trial,
    save_upper_contact_bridge_trial,
    upper_bridge_radius_mm,
    upper_bridge_span_mm,
)


class UpperContactBridgeTrialTests(unittest.TestCase):
    def test_span_and_role_radius(self):
        self.assertEqual(upper_bridge_span_mm(0.066), 0.366)
        self.assertEqual(upper_bridge_span_mm(0.893), 1.193)
        self.assertEqual(upper_bridge_radius_mm("PRONG"), 0.30)
        self.assertEqual(upper_bridge_radius_mm("SUPPORT"), 0.45)

    def test_script_compiles_and_preserves_originals(self):
        script = build_upper_contact_bridge_trial_script(Path("upper_bridge.json"))
        compile(script, "upper_contact_bridge_trial.py", "exec")
        self.assertIn("rs.AddCylinder", script)
        self.assertIn("PTR_UPPER_CONTACT_BRIDGE_TRIAL", script)
        self.assertIn("Mesh.CreateFromBrep", script)
        for forbidden in ("rs.Delete", "rs.Move", "rs.Boolean", "rs.Command", "rs.Save"):
            self.assertNotIn(forbidden, script)
        self.assertIn("ORIGINAL GEOMETRY MODIFIED | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_upper_contact_bridge_trial(
                root, datetime(2026, 7, 18, 19, 0, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Upper_Contact_Bridge_Trials")
            save_upper_contact_bridge_trial(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
