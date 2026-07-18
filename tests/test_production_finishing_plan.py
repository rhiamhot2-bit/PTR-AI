"""Tests for Production Finishing Plan."""
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from utils.production_finishing_plan_generator import (
    build_production_finishing_plan_script,
    prepare_production_finishing_plan,
    prong_finishing_action,
    save_production_finishing_plan,
)

class ProductionFinishingPlanTests(unittest.TestCase):
    def test_actions(self):
        self.assertEqual(prong_finishing_action(0.70),("LENGTHEN_OR_REBUILD",0.1))
        self.assertEqual(prong_finishing_action(1.20),("KEEP_FOR_BENCH_SETTING",0.0))
        self.assertEqual(prong_finishing_action(2.80),("TRIM",0.3))

    def test_plan_only_safeguards(self):
        script=build_production_finishing_plan_script(Path("report.json"))
        compile(script,"plan.py","exec")
        self.assertIn("LENGTHEN_OR_REBUILD",script)
        self.assertIn("KEEP_GEOMETRY_INSPECT_JUNCTIONS",script)
        self.assertIn("engagement_ratio>=0.25",script)
        self.assertNotIn("rs.Command",script)
        self.assertNotIn("rs.Delete",script)
        self.assertNotIn("AddBrep",script)
        self.assertNotIn("CreateBooleanUnion",script)

    def test_save(self):
        with tempfile.TemporaryDirectory() as folder:
            path,report,script=prepare_production_finishing_plan(
                Path(folder),datetime(2026,7,19,0,10,0)
            )
            save_production_finishing_plan(path,script)
            self.assertTrue(path.exists())
            self.assertIn("Production_Finishing_Plans",str(report))

if __name__=="__main__":
    unittest.main()
