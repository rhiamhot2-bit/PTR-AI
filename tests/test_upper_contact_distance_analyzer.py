"""Tests for Upper Contact Distance Analyzer."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.upper_contact_distance_analyzer_generator import (
    build_upper_contact_distance_analyzer_script,
    classify_surface_gap,
    prepare_upper_contact_distance_analyzer,
    proposed_extension_mm,
    save_upper_contact_distance_analyzer,
)


class UpperContactDistanceAnalyzerTests(unittest.TestCase):
    def test_gap_classification_and_extension(self):
        self.assertEqual(classify_surface_gap(0.05), "VERIFY_NEAR_CONTACT")
        self.assertEqual(classify_surface_gap(0.051), "EXTENSION_CANDIDATE")
        self.assertEqual(classify_surface_gap(1.50), "EXTENSION_CANDIDATE")
        self.assertEqual(classify_surface_gap(1.501), "NEW_CONNECTION_GEOMETRY_REQUIRED")
        self.assertEqual(proposed_extension_mm(0.20), 0.35)

    def test_script_is_report_only_and_compiles(self):
        script = build_upper_contact_distance_analyzer_script(Path("upper_distances.json"))
        compile(script, "upper_contact_distances.py", "exec")
        self.assertIn("Mesh.CreateFromBrep", script)
        self.assertIn("ClosestMeshPoint", script)
        self.assertIn("direction_target_toward_seat", script)
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Boolean", "rs.Command", "rs.Save"):
            self.assertNotIn(forbidden, script)
        self.assertIn("TEMPORARY MESHES ADDED TO DOCUMENT | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_upper_contact_distance_analyzer(
                root, datetime(2026, 7, 18, 18, 45, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Upper_Contact_Distances")
            save_upper_contact_distance_analyzer(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
