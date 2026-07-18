"""Tests for Full Metal Assembly Boolean Rehearsal."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.full_metal_assembly_boolean_rehearsal_generator import (
    build_full_metal_assembly_boolean_rehearsal_script,
    classify_full_assembly,
    prepare_full_metal_assembly_boolean_rehearsal,
    save_full_metal_assembly_boolean_rehearsal,
)

class FullMetalAssemblyTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_full_assembly(1,True,0),"FULL_METAL_ASSEMBLY_BOOLEAN_REHEARSAL_PASSED")
        self.assertEqual(classify_full_assembly(0,False,-1),"FULL_ASSEMBLY_BOOLEAN_FAILED")
        self.assertEqual(classify_full_assembly(2,False,-1),"MULTIPLE_ASSEMBLY_RESULTS")
        self.assertEqual(classify_full_assembly(1,False,0),"ASSEMBLY_NOT_CLOSED")
        self.assertEqual(classify_full_assembly(1,True,2),"ASSEMBLY_HAS_NAKED_EDGES")

    def test_eight_duplicate_script(self):
        script=build_full_metal_assembly_boolean_rehearsal_script(Path("report.json"))
        compile(script,"full_assembly.py","exec")
        self.assertIn("len(duplicates)==8",script)
        self.assertIn("brep.DuplicateBrep()",script)
        self.assertIn("Brep.CreateBooleanUnion",script)
        self.assertIn("sc.doc.Objects.AddBrep",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)
        self.assertIn("BOOLEAN USED ORIGINAL DOCUMENT IDS | NO",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_full_metal_assembly_boolean_rehearsal(
                Path(folder),datetime(2026,7,18,23,0,0)
            )
            save_full_metal_assembly_boolean_rehearsal(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Full_Metal_Assembly_Boolean_Rehearsals",str(report))

if __name__=="__main__":
    unittest.main()
