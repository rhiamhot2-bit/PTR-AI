"""Tests for Curved Support Contact Validator."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.curved_support_contact_validator_generator import (
    build_curved_support_contact_validator_script,
    classify_support,
    prepare_curved_support_contact_validator,
    save_curved_support_contact_validator,
)

class CurvedSupportValidatorTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_support(True,0,.20,.20),"READY_FOR_SUPPORT_BOOLEAN_REHEARSAL")
        self.assertEqual(classify_support(False,0,.20,.20),"INVALID_SUPPORT_SOLID")
        self.assertEqual(classify_support(True,1,.20,.20),"INVALID_SUPPORT_SOLID")
        self.assertEqual(classify_support(True,0,.10,.20),"TOP_CONTACT_TOO_SHALLOW")
        self.assertEqual(classify_support(True,0,.20,.10),"BOTTOM_CONTACT_TOO_SHALLOW")

    def test_report_only_script(self):
        script=build_curved_support_contact_validator_script(Path("report.json"))
        compile(script,"support_check.py","exec")
        self.assertIn("VolumeMassProperties.Compute",script)
        self.assertIn("Brep.CreateBooleanIntersection",script)
        self.assertIn("MIN_CONTACT_DEPTH_MM=0.15",script)
        self.assertNotIn("sc.doc.Objects.AddBrep",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_curved_support_contact_validator(
                Path(folder),datetime(2026,7,18,22,20,0)
            )
            save_curved_support_contact_validator(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Curved_Support_Contact_Reports",str(report))

if __name__=="__main__":
    unittest.main()
