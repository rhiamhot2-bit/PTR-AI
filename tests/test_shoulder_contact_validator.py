import tempfile
import unittest
from pathlib import Path

from utils.shoulder_contact_validator import (
    build_shoulder_contact_validator_script,
    prepare_shoulder_contact_validator,
    save_shoulder_contact_validator,
)


class ShoulderContactValidatorTests(unittest.TestCase):
    def test_generated_script_is_report_only(self):
        script = build_shoulder_contact_validator_script(Path("C:/Memory/report.json"))
        compile(script, "shoulder_contact_check.py", "exec")

        self.assertIn("SHOULDER_CONTACT_REVIEW_REQUIRED", script)
        self.assertIn("SHOULDER_CONTACT_BLOCKED", script)
        self.assertIn("production_export_allowed", script)
        self.assertIn("geometry_modified", script)
        self.assertNotIn("BooleanUnion", script)
        self.assertNotIn("Objects.Add", script)
        self.assertNotIn("Objects.Delete", script)
        self.assertNotIn("Write3dmFile", script)

    def test_generated_script_checks_required_contacts_and_symmetry(self):
        script = build_shoulder_contact_validator_script(Path("C:/Memory/report.json"))

        for name in (
            "PTR_SHOULDER_LEFT",
            "PTR_SHOULDER_RIGHT",
            "PTR_RING_BAND_SIZE_52",
            "PTR_OVAL_STONE_SEAT_CONCEPT",
        ):
            self.assertIn(name, script)
        self.assertIn("contact_candidate", script)
        self.assertIn("mirror_x_delta_mm", script)
        self.assertIn("bbox_gap_mm", script)

    def test_prepare_and_save_use_unique_audit_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_root = Path(temp_dir)
            script_path, report_path, script = prepare_shoulder_contact_validator(memory_root)
            save_shoulder_contact_validator(script_path, script)

            self.assertTrue(script_path.exists())
            self.assertEqual(script_path.parent.name, "Rhino_Scripts")
            self.assertEqual(report_path.parent.name, "Shoulder_Contact_Audits")
            self.assertIn(str(report_path).replace("\\", "/"), script)


if __name__ == "__main__":
    unittest.main()
