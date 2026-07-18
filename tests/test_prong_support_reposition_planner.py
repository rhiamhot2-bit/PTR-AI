"""Tests for Prong and Support Reposition Planner."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_support_reposition_planner_generator import (
    build_prong_support_reposition_planner_script,
    prepare_prong_support_reposition_planner,
    required_prong_engagement_mm,
    save_prong_support_reposition_planner,
)

class RepositionPlannerTests(unittest.TestCase):
    def test_engagement_rule(self):
        self.assertEqual(required_prong_engagement_mm(1.0), 0.25)
        self.assertEqual(required_prong_engagement_mm(0.8), 0.20)

    def test_script_compiles_and_is_report_only(self):
        script = build_prong_support_reposition_planner_script(Path("plan.json"))
        compile(script, "reposition_plan.py", "exec")
        self.assertIn("PRONG_OUTWARD_TILT_DEG = 11.0", script)
        self.assertIn("MIN_PRONG_ENGAGEMENT_RATIO = 0.25", script)
        self.assertIn("top_contact=100% | bottom_contact=100%", script)
        self.assertIn("BRIDGE CONNECTORS | FALLBACK ONLY", script)
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Rotate", "rs.Boolean", "rs.Command"):
            self.assertNotIn(forbidden, script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path, report, script = prepare_prong_support_reposition_planner(
                root, datetime(2026, 7, 18, 19, 15, 0)
            )
            self.assertEqual(report.parent, root / "Prong_Support_Reposition_Plans")
            save_prong_support_reposition_planner(path, script)
            self.assertTrue(path.exists())

if __name__ == "__main__":
    unittest.main()
