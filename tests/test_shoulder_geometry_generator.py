import tempfile
import unittest
from pathlib import Path

from utils.shoulder_geometry_generator import (
    build_shoulder_geometry_script,
    prepare_shoulder_geometry_paths,
)


class ShoulderGeometryGeneratorTests(unittest.TestCase):
    def test_script_creates_two_separate_review_shoulders(self) -> None:
        script = build_shoulder_geometry_script(Path("C:/PTR/shoulder-build.json"))
        compile(script, "<shoulder-geometry>", "exec")
        self.assertTrue(script.startswith("# -*- coding: utf-8 -*-"))
        self.assertIn("ptr-shoulder-loft-v4", script)
        self.assertIn("PTR_SHOULDER_LEFT", script)
        self.assertIn("PTR_SHOULDER_RIGHT", script)
        self.assertNotIn("rs.AddPipe", script)
        self.assertIn("Rhino.Geometry.Brep.CreateFromLoft", script)
        self.assertIn("Rhino.Geometry.Ellipse", script)
        self.assertIn("DivideByCount", script)
        self.assertIn("CapPlanarHoles", script)
        self.assertIn("rs.AddInterpCurve", script)
        self.assertIn('"STONE_SEAT" in item["upper"]', script)
        self.assertIn("band_surface_z", script)
        self.assertIn("SECTION_STATIONS = (0.0, 0.25, 0.50, 0.75, 1.0)", script)
        self.assertIn("WIDTH_RADII_MM = (0.82, 0.78, 0.68, 0.58, 0.50)", script)
        self.assertIn("DEPTH_RADII_MM = (0.52, 0.50, 0.46, 0.42, 0.38)", script)
        self.assertIn("control_3", script)
        self.assertIn('"band_anchor_in_bbox"', script)
        self.assertIn('"setting_anchor_in_bbox"', script)
        self.assertIn('"construction_method": "elliptical_section_loft"', script)
        self.assertIn('"clearance_method": "bounding_box_conservative"', script)
        self.assertIn('"minimum_clearance_target_mm": MIN_CLEARANCE_MM', script)
        self.assertIn('"clearance_checks": clearance_checks', script)
        self.assertIn('"curve_control_count": 5', script)
        self.assertIn("SHOULDER_GEOMETRY_REVIEW_REQUIRED", script)

    def test_script_preserves_production_safety_boundary(self) -> None:
        script = build_shoulder_geometry_script(Path("C:/PTR/shoulder-build.json"))
        self.assertIn('"boolean_executed": False', script)
        self.assertIn('"source_geometry_modified": False', script)
        self.assertIn('"production_export_allowed": False', script)
        self.assertNotIn("BooleanUnion", script)
        self.assertNotIn("CreateBooleanUnion", script)
        self.assertNotIn("Write3dmFile", script)
        self.assertNotIn("SaveAs", script)

    def test_paths_are_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, report = prepare_shoulder_geometry_paths(Path(temp))
            self.assertEqual(script.suffix, ".py")
            self.assertEqual(report.suffix, ".json")
            self.assertEqual(report.parent.name, "Shoulder_Builds")
            self.assertNotEqual(script.parent, report.parent)


if __name__ == "__main__":
    unittest.main()
