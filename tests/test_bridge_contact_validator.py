"""Tests for Bridge Contact Validator."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.bridge_contact_validator_generator import (
    build_bridge_contact_validator_script,
    classify_bridge_contact,
    prepare_bridge_contact_validator,
    save_bridge_contact_validator,
)


class BridgeContactValidatorTests(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(classify_bridge_contact(False, 0, True, True, 0.15), "INVALID_BRIDGE_SOLID")
        self.assertEqual(classify_bridge_contact(True, 1, True, True, 0.15), "INVALID_BRIDGE_SOLID")
        self.assertEqual(classify_bridge_contact(True, 0, False, True, 0.15), "NO_SUPPORT_CONTACT")
        self.assertEqual(classify_bridge_contact(True, 0, True, False, 0.15), "NO_BAND_CONTACT")
        self.assertEqual(classify_bridge_contact(True, 0, True, True, 0.099), "OVERLAP_TOO_SHALLOW")
        self.assertEqual(classify_bridge_contact(True, 0, True, True, 0.10), "READY_FOR_BOOLEAN_REHEARSAL")

    def test_script_is_report_only_and_compiles(self):
        script = build_bridge_contact_validator_script(Path("bridge_contact.json"))
        compile(script, "bridge_contact_validator.py", "exec")
        self.assertIn("BrepBrep", script)
        self.assertIn("DuplicateNakedEdgeCurves", script)
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Boolean", "rs.Command", "rs.Save"):
            self.assertNotIn(forbidden, script)
        self.assertIn("GEOMETRY MODIFIED | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_bridge_contact_validator(
                root, datetime(2026, 7, 18, 17, 45, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Bridge_Contact_Reports")
            save_bridge_contact_validator(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
