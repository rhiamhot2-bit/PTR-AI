"""Tests for Upper Setting Contact Validator."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.upper_setting_contact_validator_generator import (
    build_upper_setting_contact_validator_script,
    classify_upper_contact,
    prepare_upper_setting_contact_validator,
    save_upper_setting_contact_validator,
)


class UpperSettingContactValidatorTests(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(classify_upper_contact(False, False, 0, 0), "INVALID_METAL_SOLID")
        self.assertEqual(classify_upper_contact(True, False, 0, 0), "NO_SURFACE_INTERSECTION")
        self.assertEqual(classify_upper_contact(True, True, 0, 0), "CONTACT_ONLY_NO_VOLUME_OVERLAP")
        self.assertEqual(classify_upper_contact(True, True, 0.2, 0.099), "OVERLAP_TOO_SHALLOW")
        self.assertEqual(classify_upper_contact(True, True, 0.2, 0.10), "READY_FOR_UPPER_BOOLEAN_REHEARSAL")

    def test_script_is_report_only_and_compiles(self):
        script = build_upper_setting_contact_validator_script(Path("upper_contact.json"))
        compile(script, "upper_setting_contact_validator.py", "exec")
        self.assertIn("Brep.CreateBooleanIntersection", script)
        self.assertIn("VolumeMassProperties.Compute", script)
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Boolean", "rs.Command", "rs.Save"):
            self.assertNotIn(forbidden, script)
        self.assertIn("BOOLEAN GEOMETRY ADDED TO DOCUMENT | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_upper_setting_contact_validator(
                root, datetime(2026, 7, 18, 18, 30, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Upper_Setting_Contact_Reports")
            save_upper_setting_contact_validator(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
