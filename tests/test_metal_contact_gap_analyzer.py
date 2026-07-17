"""Tests for the metal contact gap analyzer."""

import math
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.metal_contact_gap_analyzer import (
    bbox_gap_mm,
    build_metal_contact_gap_script,
    classify_gap_mm,
    is_source_metal_name,
    prepare_metal_contact_gap_analyzer,
    save_metal_contact_gap_analyzer,
)


class MetalContactGapAnalyzerTests(unittest.TestCase):
    def test_source_name_filter(self):
        self.assertTrue(is_source_metal_name("PTR_RING_BAND_SIZE_52"))
        self.assertTrue(is_source_metal_name("PTR_SHOULDER_LEFT"))
        self.assertFalse(is_source_metal_name("PTR_STONE_PLACEHOLDER_8x6"))
        self.assertFalse(is_source_metal_name("PTR_GIRDLE_GUIDE_1"))
        self.assertFalse(is_source_metal_name("PTR_PRONG_1_REHEARSAL_COPY"))

    def test_bbox_gap(self):
        first = ((0, 0, 0), (1, 1, 1))
        self.assertEqual(bbox_gap_mm(first, ((0.5, 0, 0), (2, 1, 1))), 0)
        self.assertEqual(bbox_gap_mm(first, ((1.25, 0, 0), (2, 1, 1))), 0.25)
        self.assertAlmostEqual(
            bbox_gap_mm(first, ((1.3, 1.4, 0), (2, 2, 1))),
            math.sqrt(0.3 ** 2 + 0.4 ** 2),
        )

    def test_gap_classification(self):
        self.assertEqual(classify_gap_mm(0.05), "contact")
        self.assertEqual(classify_gap_mm(0.051), "near")
        self.assertEqual(classify_gap_mm(0.50), "near")
        self.assertEqual(classify_gap_mm(0.501), "disconnected")

    def test_script_is_report_only_and_compiles(self):
        script = build_metal_contact_gap_script(Path("audit.json"))
        compile(script, "metal_contact_gaps.py", "exec")
        for forbidden in ("rs.Add", "rs.Copy", "rs.Delete", "rs.Move", "rs.Boolean", "rs.Command"):
            self.assertNotIn(forbidden, script)
        self.assertIn("connected_components", script)
        self.assertIn("Bounding-box proximity is not proof", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_metal_contact_gap_analyzer(
                root, datetime(2026, 7, 17, 22, 0, 0)
            )
            self.assertEqual(script_path.parent, root / "Metal_Contact_Gaps")
            self.assertEqual(report_path.suffix, ".json")
            save_metal_contact_gap_analyzer(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
