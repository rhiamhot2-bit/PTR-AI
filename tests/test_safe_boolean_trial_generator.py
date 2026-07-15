import tempfile
import unittest
from pathlib import Path

from utils.safe_boolean_trial_generator import (
    GENERATOR_VERSION,
    build_safe_boolean_trial_script,
    prepare_safe_boolean_trial_paths,
)


class SafeBooleanTrialGeneratorTests(unittest.TestCase):
    def test_script_is_staged_and_non_destructive(self):
        script = build_safe_boolean_trial_script(Path("boolean_trial.json"))
        compile(script, "<safe-boolean-trial>", "exec")
        self.assertEqual(GENERATOR_VERSION, "ptr-safe-boolean-trial-v1")
        self.assertIn("CreateBooleanUnion", script)
        self.assertIn('"BAND_SHOULDERS"', script)
        self.assertIn('"SETTING_METAL"', script)
        self.assertIn('"FINAL_ASSEMBLY"', script)
        self.assertIn("DuplicateBrep", script)
        self.assertNotIn("DeleteObject", script)
        self.assertNotIn("ExportSelected", script)

    def test_script_excludes_references_and_validates_results(self):
        script = build_safe_boolean_trial_script(Path("boolean_trial.json"))
        self.assertIn("STONE_PLACEHOLDER", script)
        self.assertIn("GIRDLE_GUIDE", script)
        self.assertIn("IsValid", script)
        self.assertIn("IsSolid", script)
        self.assertIn("DuplicateNakedEdgeCurves", script)
        self.assertIn('"production_export_allowed": False', script)
        self.assertIn('"source_geometry_modified": False', script)

    def test_paths_use_boolean_trials_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path, audit_path = prepare_safe_boolean_trial_paths(Path(temp_dir))
            self.assertEqual(script_path.parent.name, "Rhino_Scripts")
            self.assertEqual(audit_path.parent.name, "Boolean_Trials")
            self.assertTrue(script_path.name.endswith("_safe_boolean_trial.py"))
            self.assertTrue(audit_path.name.endswith("_safe_boolean_trial.json"))


if __name__ == "__main__":
    unittest.main()
