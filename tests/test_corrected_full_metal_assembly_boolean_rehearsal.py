"""Tests for corrected Full Metal Assembly Boolean Rehearsal."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.corrected_full_metal_assembly_boolean_rehearsal_generator import (
    build_corrected_full_metal_assembly_boolean_rehearsal_script,
    classify_corrected_full_assembly,
    prepare_corrected_full_metal_assembly_boolean_rehearsal,
    save_corrected_full_metal_assembly_boolean_rehearsal,
)

class CorrectedFullMetalAssemblyTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_corrected_full_assembly(1,True,0),"CORRECTED_FULL_METAL_ASSEMBLY_BOOLEAN_REHEARSAL_PASSED")
        self.assertEqual(classify_corrected_full_assembly(0,False,-1),"CORRECTED_FULL_ASSEMBLY_BOOLEAN_FAILED")
        self.assertEqual(classify_corrected_full_assembly(2,False,-1),"MULTIPLE_CORRECTED_ASSEMBLY_RESULTS")
        self.assertEqual(classify_corrected_full_assembly(1,False,0),"CORRECTED_ASSEMBLY_NOT_CLOSED")
        self.assertEqual(classify_corrected_full_assembly(1,True,2),"CORRECTED_ASSEMBLY_HAS_NAKED_EDGES")

    def test_eight_duplicate_script_uses_corrected_prongs(self):
        script=build_corrected_full_metal_assembly_boolean_rehearsal_script(Path("report.json"))
        compile(script,"corrected_full_assembly.py","exec")
        self.assertIn('_LENGTH_CORRECTION_TRIAL',script)
        self.assertIn("len(duplicates)==8",script)
        self.assertIn("brep.DuplicateBrep()",script)
        self.assertIn("Brep.CreateBooleanUnion",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)
        self.assertIn("BOOLEAN USED ORIGINAL DOCUMENT IDS | NO",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_corrected_full_metal_assembly_boolean_rehearsal(Path(folder),datetime(2026,7,18,23,45,0))
            save_corrected_full_metal_assembly_boolean_rehearsal(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Corrected_Full_Metal_Assembly_Boolean_Rehearsals",str(report))

if __name__=="__main__":
    unittest.main()
