"""Tests for Clean Production Candidate."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.clean_production_candidate_generator import (
    build_clean_production_candidate_script,
    candidate_status,
    prepare_clean_production_candidate,
    save_clean_production_candidate,
)

class CleanProductionCandidateTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(candidate_status(1,True,0,10.0,False),"PRODUCTION_CANDIDATE_REVIEW_CREATED")
        self.assertEqual(candidate_status(2,True,0,10.0,False),"PRODUCTION_CANDIDATE_BLOCKED_SOURCE_COUNT")
        self.assertEqual(candidate_status(1,False,0,10.0,False),"PRODUCTION_CANDIDATE_BLOCKED_TOPOLOGY")
        self.assertEqual(candidate_status(1,True,0,0.0,False),"PRODUCTION_CANDIDATE_BLOCKED_VOLUME")
        self.assertEqual(candidate_status(1,True,0,10.0,True),"PRODUCTION_CANDIDATE_BLOCKED_STONE_COLLISION")

    def test_review_only_script(self):
        script=build_clean_production_candidate_script(Path("report.json"))
        compile(script,"candidate.py","exec")
        self.assertIn("source_brep.DuplicateBrep()",script)
        self.assertIn('SetUserString("PTR_EXPORT_ALLOWED","NO")',script)
        self.assertIn('SetUserString("PTR_STONE_INCLUDED","NO")',script)
        self.assertIn("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED",script)
        self.assertNotIn("rs.Command",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("CreateBooleanUnion",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_clean_production_candidate(
                Path(folder),datetime(2026,7,18,23,40,0)
            )
            save_clean_production_candidate(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Production_Candidate_Reviews",str(report))

if __name__=="__main__":
    unittest.main()
