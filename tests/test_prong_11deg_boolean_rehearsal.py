"""Tests for Prong 11 Degree Boolean Rehearsal."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.prong_11deg_boolean_rehearsal_generator import (
    build_prong_11deg_boolean_rehearsal_script,
    classify_boolean_rehearsal,
    prepare_prong_11deg_boolean_rehearsal,
    save_prong_11deg_boolean_rehearsal,
)

class Prong11BooleanTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_boolean_rehearsal(1,True,0),"PRONG_11DEG_BOOLEAN_REHEARSAL_PASSED")
        self.assertEqual(classify_boolean_rehearsal(0,False,-1),"BOOLEAN_REHEARSAL_FAILED")
        self.assertEqual(classify_boolean_rehearsal(2,False,-1),"MULTIPLE_BOOLEAN_RESULTS")
        self.assertEqual(classify_boolean_rehearsal(1,False,0),"RESULT_NOT_CLOSED")
        self.assertEqual(classify_boolean_rehearsal(1,True,2),"RESULT_HAS_NAKED_EDGES")

    def test_copy_only_script(self):
        script=build_prong_11deg_boolean_rehearsal_script(Path("report.json"))
        compile(script,"prong_boolean.py","exec")
        self.assertIn("source_brep.DuplicateBrep()",script)
        self.assertIn("Brep.CreateBooleanUnion",script)
        self.assertIn("sc.doc.Objects.AddBrep",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)
        self.assertNotIn("rs.RotateObject",script)
        self.assertIn("BOOLEAN USED ORIGINAL DOCUMENT IDS | NO",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_prong_11deg_boolean_rehearsal(
                Path(folder),datetime(2026,7,18,21,40,0)
            )
            save_prong_11deg_boolean_rehearsal(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Prong_11Deg_Boolean_Rehearsals",str(report))

if __name__=="__main__":
    unittest.main()
