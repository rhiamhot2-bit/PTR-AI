import tempfile
import unittest
from pathlib import Path

from utils.production_readiness_generator import (
    build_production_readiness_script,
    prepare_production_audit_paths,
)


class ProductionReadinessTests(unittest.TestCase):
    def test_script_is_report_only_and_blocks_production_export(self) -> None:
        script = build_production_readiness_script(Path("C:/PTR/production.json"))
        compile(script, "<production-readiness>", "exec")
        self.assertIn("NOT_PRODUCTION_READY", script)
        self.assertIn("MANUAL_REVIEW_REQUIRED", script)
        self.assertIn("production_export_allowed", script)
        self.assertIn("METAL SOLIDS", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)
        self.assertIn("STONE_PLACEHOLDER", script)
        self.assertIn("GIRDLE_GUIDE", script)
        self.assertNotIn("BooleanUnion", script)
        self.assertNotIn("SaveAs", script)
        self.assertNotIn("Write3dmFile", script)
        self.assertNotIn(".stl", script.lower())

    def test_multiple_metal_solids_are_a_blocker(self) -> None:
        script = build_production_readiness_script(Path("C:/PTR/production.json"))
        self.assertIn('if len(metal_rows) > 1:', script)
        self.assertIn('"production_export_allowed": False', script)
        self.assertIn('"blockers": blockers', script)

    def test_paths_are_unique_and_separate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, audit = prepare_production_audit_paths(Path(temp))
            self.assertEqual(script.suffix, ".py")
            self.assertEqual(audit.suffix, ".json")
            self.assertNotEqual(script.parent, audit.parent)
            self.assertEqual(audit.parent.name, "Production_Audits")


if __name__ == "__main__":
    unittest.main()
