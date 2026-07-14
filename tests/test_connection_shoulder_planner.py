import tempfile
import unittest
from pathlib import Path

from utils.connection_shoulder_planner import (
    build_connection_shoulder_plan_script,
    prepare_shoulder_plan_paths,
)


class ConnectionShoulderPlannerTests(unittest.TestCase):
    def test_script_is_report_only(self) -> None:
        script = build_connection_shoulder_plan_script(
            Path("C:/PTR/shoulder-plan.json")
        )
        compile(script, "<connection-shoulder-plan>", "exec")
        self.assertTrue(script.startswith("# -*- coding: utf-8 -*-"))
        self.assertIn("SHOULDER_PLAN_REVIEW_REQUIRED", script)
        self.assertIn("SHOULDER_BRIDGE_CANDIDATE", script)
        self.assertIn('"geometry_created": False', script)
        self.assertIn('"boolean_executed": False', script)
        self.assertIn('"document_modified": False', script)
        self.assertIn("No geometry was modified.", script)
        self.assertNotIn("BooleanUnion", script)
        self.assertNotIn("CreateBooleanUnion", script)
        self.assertNotIn("Objects.Add", script)
        self.assertNotIn("rs.Add", script)
        self.assertNotIn("Objects.Delete", script)
        self.assertNotIn("Write3dmFile", script)

    def test_script_proposes_symmetric_connection_bridges(self) -> None:
        script = build_connection_shoulder_plan_script(
            Path("C:/PTR/shoulder-plan.json")
        )
        self.assertIn('("LEFT", -1.0), ("RIGHT", 1.0)', script)
        self.assertIn("minimum_overlap_each_end_mm", script)
        self.assertIn("starting_width_mm", script)
        self.assertIn("starting_thickness_mm", script)
        self.assertIn("requires_surface_projection", script)

    def test_paths_are_unique_and_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, report = prepare_shoulder_plan_paths(Path(temp))
            self.assertEqual(script.suffix, ".py")
            self.assertEqual(report.suffix, ".json")
            self.assertNotEqual(script.parent, report.parent)
            self.assertEqual(report.parent.name, "Shoulder_Plans")


if __name__ == "__main__":
    unittest.main()
