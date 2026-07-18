"""Tests for Production Finishing Audit."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.production_finishing_audit_generator import (
    build_production_finishing_audit_script,
    finishing_status,
    prepare_production_finishing_audit,
    save_production_finishing_audit,
)

class ProductionFinishingAuditTests(unittest.TestCase):
    def test_status_gates(self):
        self.assertEqual(finishing_status(1,4,2,True,0,False),"FINISHING_AUDIT_REVIEW_REQUIRED")
        self.assertEqual(finishing_status(0,4,2,True,0,False),"FINISHING_AUDIT_BLOCKED_CANDIDATE")
        self.assertEqual(finishing_status(1,3,2,True,0,False),"FINISHING_AUDIT_BLOCKED_MEMBER_COUNT")
        self.assertEqual(finishing_status(1,4,2,False,0,False),"FINISHING_AUDIT_BLOCKED_TOPOLOGY")
        self.assertEqual(finishing_status(1,4,2,True,0,True),"FINISHING_AUDIT_BLOCKED_STONE_COLLISION")

    def test_report_only_safeguards(self):
        script=build_production_finishing_audit_script(Path("report.json"))
        compile(script,"audit.py","exec")
        self.assertIn("MIN_PRONG_TRIM_MM = 0.80",script)
        self.assertIn("JUNCTION_REVIEW_REQUIRED",script)
        self.assertNotIn("rs.Command",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("AddBrep",script)
        self.assertNotIn("CreateBooleanUnion",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_production_finishing_audit(
                Path(folder),datetime(2026,7,18,23,50,0)
            )
            save_production_finishing_audit(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Production_Finishing_Audits",str(report))

if __name__=="__main__":
    unittest.main()
