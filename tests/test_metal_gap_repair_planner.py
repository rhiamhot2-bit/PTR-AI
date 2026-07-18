"""Tests for the Metal Gap Repair Planner."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.metal_gap_repair_planner_generator import (
    build_metal_gap_repair_planner_script,
    classify_repair,
    extension_mm,
    is_repair_plan_metal_name,
    prepare_metal_gap_repair_planner,
    save_metal_gap_repair_planner,
)


class MetalGapRepairPlannerTests(unittest.TestCase):
    def test_name_filter(self):
        self.assertTrue(is_repair_plan_metal_name("PTR_BASKET_SUPPORT_1"))
        self.assertTrue(is_repair_plan_metal_name("PTR_RING_BAND_SIZE_52"))
        self.assertFalse(is_repair_plan_metal_name("PTR_STONE_PLACEHOLDER_8x6"))
        self.assertFalse(is_repair_plan_metal_name("PTR_PRONG_1_REHEARSAL_COPY"))

    def test_repair_classification(self):
        self.assertEqual(classify_repair(0.0, True), "NO_REPAIR_INTERSECTING")
        self.assertEqual(classify_repair(0.05, False), "VERIFY_CONTACT")
        self.assertEqual(classify_repair(0.695, False), "EXTENSION_CANDIDATE")
        self.assertEqual(classify_repair(1.50, False), "EXTENSION_CANDIDATE")
        self.assertEqual(classify_repair(1.501, False), "NEW_CONNECTION_GEOMETRY_REQUIRED")
        self.assertEqual(extension_mm(0.695), 0.845)

    def test_generated_script_is_report_only_and_compiles(self):
        script = build_metal_gap_repair_planner_script(Path("repair.json"))
        compile(script, "metal_gap_repair_plan.py", "exec")
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Boolean", "rs.Command"):
            self.assertNotIn(forbidden, script)
        self.assertIn("direction_from_source_toward_target", script)
        self.assertIn("GEOMETRY MODIFIED | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_metal_gap_repair_planner(
                root, datetime(2026, 7, 18, 17, 15, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Metal_Gap_Repair_Plans")
            save_metal_gap_repair_planner(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
