"""Tests for Corrected Production Finishing Audit."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.corrected_production_finishing_audit_generator import (
    build_corrected_production_finishing_audit_script,
    corrected_finishing_status,
    prepare_corrected_production_finishing_audit,
    save_corrected_production_finishing_audit,
)

class CorrectedProductionFinishingAuditTests(unittest.TestCase):
    def test_status_gates(self):
        self.assertEqual(corrected_finishing_status(1,4,2,True,0,False,True),"CORRECTED_FINISHING_AUDIT_REVIEW_REQUIRED")
        self.assertEqual(corrected_finishing_status(0,4,2,True,0,False,True),"CORRECTED_FINISHING_AUDIT_BLOCKED_CANDIDATE")
        self.assertEqual(corrected_finishing_status(1,3,2,True,0,False,True),"CORRECTED_FINISHING_AUDIT_BLOCKED_MEMBER_COUNT")
        self.assertEqual(corrected_finishing_status(1,4,2,True,0,False,False),"CORRECTED_FINISHING_AUDIT_BLOCKED_PRONG_FINISH")

    def test_report_only_and_corrected_inputs(self):
        script=build_corrected_production_finishing_audit_script(Path("report.json"))
        compile(script,"audit.py","exec")
        self.assertIn("PTR_CORRECTED_PRODUCTION_CANDIDATE_REVIEW_ONLY",script)
        self.assertIn("_LENGTH_CORRECTION_TRIAL",script)
        self.assertIn("TARGET_OUTWARD_TILT_DEG = 11.0",script)
        self.assertIn("MIN_PRONG_TRIM_MM = 0.80",script)
        for forbidden in ("rs.Command","rs.Delete","AddBrep","CreateBooleanUnion"):
            self.assertNotIn(forbidden,script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_corrected_production_finishing_audit(Path(folder),datetime(2026,7,19,0,20,0))
            save_corrected_production_finishing_audit(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Corrected_Production_Finishing_Audits",str(report))

if __name__=="__main__": unittest.main()
