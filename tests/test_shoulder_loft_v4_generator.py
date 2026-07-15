import tempfile
import unittest
from pathlib import Path

from utils.shoulder_loft_v4_generator import (
    GENERATOR_VERSION,
    build_shoulder_loft_v4_script,
    prepare_shoulder_loft_v4_paths,
)


class ShoulderLoftV4GeneratorTests(unittest.TestCase):
    def test_script_contains_real_contact_audit(self):
        script = build_shoulder_loft_v4_script(Path("shoulder_loft_v4.json"))

        compile(script, "<shoulder-loft-v4>", "exec")
        self.assertEqual(GENERATOR_VERSION, "ptr-shoulder-loft-v4-contact-audit")
        self.assertIn("Intersection.BrepBrep", script)
        self.assertIn("band_surface_intersection", script)
        self.assertIn("setting_surface_intersections", script)
        self.assertIn("all_contacts_verified", script)
        self.assertIn("SHOULDER_LOFT_V4_CONTACT_BLOCKED", script)

    def test_script_preserves_review_only_safety(self):
        script = build_shoulder_loft_v4_script(Path("shoulder_loft_v4.json"))

        self.assertIn("BOOLEAN | NOT EXECUTED", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)
        self.assertIn('"production_export_allowed"] = False', script)
        self.assertNotIn("CreateBooleanUnion", script)
        self.assertNotIn("ExportSelected", script)

    def test_paths_use_dedicated_report_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path, report_path = prepare_shoulder_loft_v4_paths(
                Path(temp_dir)
            )

            self.assertEqual(script_path.parent.name, "Rhino_Scripts")
            self.assertEqual(report_path.parent.name, "Shoulder_Loft_v4")
            self.assertTrue(script_path.name.endswith("_shoulder_loft_v4.py"))
            self.assertTrue(report_path.name.endswith("_shoulder_loft_v4.json"))


if __name__ == "__main__":
    unittest.main()
