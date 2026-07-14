import tempfile
import unittest
from pathlib import Path

from utils.geometry_join_planner import (
    build_geometry_join_plan_script,
    prepare_join_plan_paths,
)


class GeometryJoinPlannerTests(unittest.TestCase):
    def test_script_is_report_only(self) -> None:
        script = build_geometry_join_plan_script(Path("C:/PTR/join-plan.json"))
        compile(script, "<geometry-join-plan>", "exec")
        self.assertTrue(script.startswith("# -*- coding: utf-8 -*-"))
        self.assertIn("JOIN_PLAN_REVIEW_REQUIRED", script)
        self.assertIn("CONTACT_CANDIDATE", script)
        self.assertIn('"boolean_executed": False', script)
        self.assertIn('"document_modified": False', script)
        self.assertIn("No geometry was modified.", script)
        self.assertNotIn("BooleanUnion", script)
        self.assertNotIn("CreateBooleanUnion", script)
        self.assertNotIn("Objects.Delete", script)
        self.assertNotIn("rs.Delete", script)
        self.assertNotIn("Write3dmFile", script)

    def test_script_builds_candidate_groups_from_bbox_gap(self) -> None:
        script = build_geometry_join_plan_script(Path("C:/PTR/join-plan.json"))
        self.assertIn("bounding_box_gap", script)
        self.assertIn("proposed_join_groups", script)
        self.assertIn("requires_manual_surface_check", script)
        self.assertIn("MIN_CONTACT_TOLERANCE_MM = 0.05", script)

    def test_paths_are_unique_and_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, report = prepare_join_plan_paths(Path(temp))
            self.assertEqual(script.suffix, ".py")
            self.assertEqual(report.suffix, ".json")
            self.assertNotEqual(script.parent, report.parent)
            self.assertEqual(report.parent.name, "Join_Plans")


if __name__ == "__main__":
    unittest.main()
