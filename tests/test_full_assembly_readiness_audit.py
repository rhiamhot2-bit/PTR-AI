"""Tests for Full Assembly Readiness Audit."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.full_assembly_readiness_audit_generator import (
    build_full_assembly_readiness_audit_script,
    classify_readiness,
    prepare_full_assembly_readiness_audit,
    save_full_assembly_readiness_audit,
)

class FullAssemblyReadinessTests(unittest.TestCase):
    def test_classification(self):
        self.assertEqual(classify_readiness(1,True,0,10.0,.9,.1,False),"FULL_ASSEMBLY_READINESS_SCREEN_PASSED")
        self.assertEqual(classify_readiness(2,True,0,10.0,.9,.1,False),"INVALID_ASSEMBLY_RESULT_COUNT")
        self.assertEqual(classify_readiness(1,False,0,10.0,.9,.1,False),"INVALID_ASSEMBLY_TOPOLOGY")
        self.assertEqual(classify_readiness(1,True,0,10.0,.7,.1,False),"MEMBER_BELOW_MINIMUM")
        self.assertEqual(classify_readiness(1,True,0,10.0,.9,.8,False),"ASSEMBLY_OFF_CENTER")
        self.assertEqual(classify_readiness(1,True,0,10.0,.9,.1,True),"STONE_COLLISION_REVIEW_REQUIRED")

    def test_report_only_script(self):
        script=build_full_assembly_readiness_audit_script(Path("report.json"))
        compile(script,"readiness.py","exec")
        self.assertIn("MIN_MEMBER_DIAMETER_MM=0.80",script)
        self.assertIn("MAX_CENTER_OFFSET_MM=0.50",script)
        self.assertIn("VolumeMassProperties.Compute",script)
        self.assertIn("original_prong_ids",script)
        self.assertIn("ORIGINAL_PRONG_REFERENCE",script)
        self.assertIn("PRONG REFERENCE DIAMETERS MM",script)
        self.assertIn("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED",script)
        self.assertNotIn("sc.doc.Objects.AddBrep",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_full_assembly_readiness_audit(
                Path(folder),datetime(2026,7,18,23,20,0)
            )
            save_full_assembly_readiness_audit(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Full_Assembly_Readiness_Audits",str(report))

if __name__=="__main__":
    unittest.main()
