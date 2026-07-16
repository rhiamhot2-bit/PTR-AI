"""Tests for the Metal Union Readiness Validator generator."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.metal_union_readiness_generator import (
    bbox_gap,
    build_metal_union_script,
    connected_components,
    is_metal_name,
    prepare_metal_union_validator,
)


class MetalUnionReadinessTests(unittest.TestCase):
    def test_metal_name_filter_excludes_guides_and_stone(self):
        self.assertTrue(is_metal_name("PTR_RING_BAND_SIZE_52"))
        self.assertTrue(is_metal_name("PTR_SHOULDER_LEFT"))
        self.assertTrue(is_metal_name("PTR_PRONG_1"))
        self.assertFalse(is_metal_name("PTR_STONE_PLACEHOLDER_8x6"))
        self.assertFalse(is_metal_name("PTR_GIRDLE_GUIDE_1"))
        self.assertFalse(is_metal_name("PTR_NOTES"))

    def test_bbox_contact_graph_finds_disconnected_group(self):
        touching = bbox_gap((0, 0, 0, 1, 1, 1), (1.04, 0, 0, 2, 1, 1))
        separate = bbox_gap((0, 0, 0, 1, 1, 1), (2, 0, 0, 3, 1, 1))
        self.assertAlmostEqual(touching, 0.04)
        self.assertAlmostEqual(separate, 1.0)
        components = connected_components(
            ["band", "left", "right"],
            [("band", "left")],
        )
        self.assertEqual(components, [["band", "left"], ["right"]])

    def test_script_is_safe_ironpython_and_paths_are_prepared(self):
        with tempfile.TemporaryDirectory() as folder:
            now = datetime(2026, 7, 16, 23, 30, 0, 123456)
            script_path, report_path, script = prepare_metal_union_validator(
                Path(folder), now=now
            )
            compile(script, str(script_path), "exec")
            self.assertIn('# -*- coding: utf-8 -*-', script)
            self.assertIn("io.open(REPORT_PATH", script)
            self.assertIn("METAL_UNION_BLOCKED", script)
            self.assertIn("METAL_UNION_REVIEW_REQUIRED", script)
            self.assertNotIn("rs.BooleanUnion", script)
            self.assertNotIn("rs.DeleteObject", script)
            self.assertNotIn("rs.MoveObject", script)
            self.assertNotIn("rs.Command", script)
            self.assertEqual(script_path.parent.name, "Rhino_Scripts")
            self.assertEqual(report_path.parent.name, "Metal_Union_Audits")
            rebuilt = build_metal_union_script(report_path)
            self.assertIn(str(report_path).replace("\\", "/"), rebuilt)


if __name__ == "__main__":
    unittest.main()
