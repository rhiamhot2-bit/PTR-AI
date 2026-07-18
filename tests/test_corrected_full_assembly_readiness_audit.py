"""Tests for Corrected Full Assembly Readiness Audit."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.corrected_full_assembly_readiness_audit_generator import (
    build_corrected_full_assembly_readiness_audit_script,
    classify_corrected_readiness,
    prepare_corrected_full_assembly_readiness_audit,
    save_corrected_full_assembly_readiness_audit,
)

class CorrectedFullAssemblyReadinessTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_corrected_readiness(1,True,0,10.0,.9,.1,False),"CORRECTED_FULL_ASSEMBLY_READINESS_SCREEN_PASSED")
        self.assertEqual(classify_corrected_readiness(2,True,0,10.0,.9,.1,False),"INVALID_ASSEMBLY_RESULT_COUNT")
        self.assertEqual(classify_corrected_readiness(1,False,0,10.0,.9,.1,False),"INVALID_ASSEMBLY_TOPOLOGY")
        self.assertEqual(classify_corrected_readiness(1,True,0,10.0,.7,.1,False),"MEMBER_BELOW_MINIMUM")
        self.assertEqual(classify_corrected_readiness(1,True,0,10.0,.9,.8,False),"ASSEMBLY_OFF_CENTER")
        self.assertEqual(classify_corrected_readiness(1,True,0,10.0,.9,.1,True),"STONE_COLLISION_REVIEW_REQUIRED")

    def test_report_only_script_targets_corrected_result(self):
        script=build_corrected_full_assembly_readiness_audit_script(Path("report.json"))
        compile(script,"corrected_readiness.py","exec")
        self.assertIn("PTR_CORRECTED_FULL_METAL_ASSEMBLY_BOOLEAN_RESULT_",script)
        self.assertIn("_LENGTH_CORRECTION_TRIAL",script)
        self.assertIn("MIN_MEMBER_DIAMETER_MM=0.80",script)
        self.assertIn("ORIGINAL_PRONG_REFERENCE",script)
        self.assertNotIn("sc.doc.Objects.AddBrep",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_corrected_full_assembly_readiness_audit(Path(folder),datetime(2026,7,18,23,50,0))
            save_corrected_full_assembly_readiness_audit(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Corrected_Full_Assembly_Readiness_Audits",str(report))

if __name__=="__main__":
    unittest.main()
