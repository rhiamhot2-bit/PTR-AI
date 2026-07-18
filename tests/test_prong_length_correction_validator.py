"""Tests for Prong Length Correction Validator."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_length_correction_validator_generator import (
    build_prong_length_correction_validator_script,
    correction_validation_status,
    prepare_prong_length_correction_validator,
    save_prong_length_correction_validator,
)

class ProngLengthCorrectionValidatorTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(correction_validation_status(4,True),"PRONG_LENGTH_CORRECTION_VALIDATION_READY")
        self.assertEqual(correction_validation_status(4,False),"PRONG_LENGTH_CORRECTION_VALIDATION_REVIEW_REQUIRED")
        self.assertEqual(correction_validation_status(3,True),"PRONG_LENGTH_CORRECTION_VALIDATION_BLOCKED_COUNT")

    def test_report_only(self):
        script=build_prong_length_correction_validator_script(Path("report.json"))
        compile(script,"validator.py","exec")
        self.assertIn("principal_measurements",script)
        self.assertIn("MAX_BASE_SHIFT_MM = 0.02",script)
        self.assertIn("ALLOWANCE_TOLERANCE_MM = 0.01",script)
        self.assertNotIn("rs.Command",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("AddBrep",script)
        self.assertNotIn("CreateBooleanUnion",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_prong_length_correction_validator(
                Path(folder),datetime(2026,7,19,0,50,0)
            )
            save_prong_length_correction_validator(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Prong_Length_Correction_Validation",str(report))

if __name__=="__main__":
    unittest.main()
