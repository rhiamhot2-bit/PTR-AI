"""Tests for Corrected Clean Production Candidate."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.corrected_clean_production_candidate_generator import (
    build_corrected_clean_production_candidate_script,
    corrected_candidate_status,
    prepare_corrected_clean_production_candidate,
    save_corrected_clean_production_candidate,
)

class CorrectedCleanProductionCandidateTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(corrected_candidate_status(1,True,0,10.0,False),"CORRECTED_PRODUCTION_CANDIDATE_REVIEW_CREATED")
        self.assertEqual(corrected_candidate_status(2,True,0,10.0,False),"CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_SOURCE_COUNT")
        self.assertEqual(corrected_candidate_status(1,False,0,10.0,False),"CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_TOPOLOGY")
        self.assertEqual(corrected_candidate_status(1,True,0,0.0,False),"CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_VOLUME")
        self.assertEqual(corrected_candidate_status(1,True,0,10.0,True),"CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_STONE_COLLISION")

    def test_review_copy_targets_only_corrected_result(self):
        script=build_corrected_clean_production_candidate_script(Path("report.json"))
        compile(script,"corrected_candidate.py","exec")
        self.assertIn("PTR_CORRECTED_FULL_METAL_ASSEMBLY_BOOLEAN_RESULT_",script)
        self.assertIn("source_brep.DuplicateBrep()",script)
        self.assertIn('SetUserString("PTR_EXPORT_ALLOWED","NO")',script)
        self.assertIn('SetUserString("PTR_READINESS_SCREEN","PASSED")',script)
        self.assertNotIn("CreateBooleanUnion",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("rs.MoveObject",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_corrected_clean_production_candidate(Path(folder),datetime(2026,7,19,0,10,0))
            save_corrected_clean_production_candidate(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Corrected_Production_Candidate_Reviews",str(report))

if __name__=="__main__":
    unittest.main()
