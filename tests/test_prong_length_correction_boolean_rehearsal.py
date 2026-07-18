"""Tests for Prong Length Correction Boolean Rehearsal."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_length_correction_boolean_rehearsal_generator import (
    build_prong_length_correction_boolean_rehearsal_script,
    classify_boolean_rehearsal,
    prepare_prong_length_correction_boolean_rehearsal,
    save_prong_length_correction_boolean_rehearsal,
)

class ProngLengthCorrectionBooleanTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(classify_boolean_rehearsal(1,True,0),"PRONG_LENGTH_CORRECTION_BOOLEAN_REHEARSAL_PASSED")
        self.assertEqual(classify_boolean_rehearsal(0,False,-1),"BOOLEAN_REHEARSAL_FAILED")
        self.assertEqual(classify_boolean_rehearsal(1,True,2),"RESULT_HAS_NAKED_EDGES")

    def test_copy_only(self):
        script=build_prong_length_correction_boolean_rehearsal_script(Path("report.json"))
        compile(script,"rehearsal.py","exec")
        self.assertIn('_LENGTH_CORRECTION_TRIAL")',script)
        self.assertIn("DuplicateBrep()",script)
        self.assertIn("CreateBooleanUnion",script)
        self.assertIn("BOOLEAN USED ORIGINAL DOCUMENT IDS | NO",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.Command",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_prong_length_correction_boolean_rehearsal(
                Path(folder),datetime(2026,7,19,1,20,0)
            )
            save_prong_length_correction_boolean_rehearsal(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Prong_Length_Correction_Boolean_Rehearsals",str(report))

if __name__=="__main__":
    unittest.main()
