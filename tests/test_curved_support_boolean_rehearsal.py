"""Tests for Curved Support Boolean Rehearsal."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.curved_support_boolean_rehearsal_generator import (
    build_curved_support_boolean_rehearsal_script,
    classify_support_boolean,
    prepare_curved_support_boolean_rehearsal,
    save_curved_support_boolean_rehearsal,
)

class CurvedSupportBooleanTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_support_boolean(1,True,0),"CURVED_SUPPORT_BOOLEAN_REHEARSAL_PASSED")
        self.assertEqual(classify_support_boolean(0,False,-1),"SUPPORT_BOOLEAN_REHEARSAL_FAILED")
        self.assertEqual(classify_support_boolean(2,False,-1),"MULTIPLE_BOOLEAN_RESULTS")
        self.assertEqual(classify_support_boolean(1,False,0),"RESULT_NOT_CLOSED")
        self.assertEqual(classify_support_boolean(1,True,1),"RESULT_HAS_NAKED_EDGES")

    def test_duplicate_only_script(self):
        script=build_curved_support_boolean_rehearsal_script(Path("report.json"))
        compile(script,"support_boolean.py","exec")
        self.assertIn("brep.DuplicateBrep()",script)
        self.assertIn("Brep.CreateBooleanUnion",script)
        self.assertIn("sc.doc.Objects.AddBrep",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)
        self.assertIn("BOOLEAN USED ORIGINAL DOCUMENT IDS | NO",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_curved_support_boolean_rehearsal(
                Path(folder),datetime(2026,7,18,22,40,0)
            )
            save_curved_support_boolean_rehearsal(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Curved_Support_Boolean_Rehearsals",str(report))

if __name__=="__main__":
    unittest.main()
