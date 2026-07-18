"""Tests for the Metal Contact Gap Analyzer used by !cadmetalgaps."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.metal_contact_gap_analyzer_generator import (
    build_metal_contact_gap_analyzer_script,
    classify_bbox_gap,
    is_gap_analyzer_metal_name,
    prepare_metal_contact_gap_analyzer,
    save_metal_contact_gap_analyzer,
)


class MetalContactGapAnalyzerTests(unittest.TestCase):
    def test_source_name_filter(self):
        self.assertTrue(is_gap_analyzer_metal_name("PTR_RING_BAND_SIZE_52"))
        self.assertTrue(is_gap_analyzer_metal_name("PTR_PRONG_1"))
        self.assertFalse(is_gap_analyzer_metal_name("PTR_STONE_PLACEHOLDER_8x6"))
        self.assertFalse(is_gap_analyzer_metal_name("PTR_GIRDLE_GUIDE_1"))
        self.assertFalse(is_gap_analyzer_metal_name("PTR_PRONG_1_REHEARSAL_COPY"))

    def test_gap_classification(self):
        self.assertEqual(classify_bbox_gap(0.0, True), "INTERSECTING")
        self.assertEqual(classify_bbox_gap(0.05, False), "CONTACT_CANDIDATE")
        self.assertEqual(classify_bbox_gap(0.051, False), "SMALL_GAP")
        self.assertEqual(classify_bbox_gap(0.30, False), "SMALL_GAP")
        self.assertEqual(classify_bbox_gap(0.301, False), "OPEN_GAP")

    def test_generated_script_is_report_only_and_compiles(self):
        script = build_metal_contact_gap_analyzer_script(Path("audit.json"))
        compile(script, "metal_contact_gaps.py", "exec")
        for forbidden in (
            "rs.Add",
            "rs.Copy",
            "rs.Delete",
            "rs.Move",
            "rs.Boolean",
            "rs.Command",
        ):
            self.assertNotIn(forbidden, script)
        self.assertIn("BrepBrep", script)
        self.assertIn("GEOMETRY MODIFIED | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_metal_contact_gap_analyzer(
                root, datetime(2026, 7, 18, 16, 30, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Metal_Contact_Gaps")
            save_metal_contact_gap_analyzer(script_path, script)
            self.assertTrue(script_path.exists())
            self.assertTrue(script_path.read_text(encoding="utf-8").startswith("# -*- coding: utf-8 -*-"))


if __name__ == "__main__":
    unittest.main()
