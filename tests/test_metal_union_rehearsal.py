"""Tests for the Metal Union Rehearsal generator."""

from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from utils.metal_union_rehearsal_generator import (
    build_metal_union_rehearsal_script,
    is_rehearsal_metal_name,
    prepare_metal_union_rehearsal,
    save_metal_union_rehearsal,
)


class MetalUnionRehearsalTests(unittest.TestCase):
    def test_metal_filter_excludes_stones_and_guides(self) -> None:
        self.assertTrue(is_rehearsal_metal_name("PTR_RING_BAND_SIZE_52"))
        self.assertTrue(is_rehearsal_metal_name("PTR_SHOULDER_LEFT"))
        self.assertTrue(is_rehearsal_metal_name("PTR_PRONG_1"))
        self.assertFalse(is_rehearsal_metal_name("PTR_STONE_PLACEHOLDER_8x6"))
        self.assertFalse(is_rehearsal_metal_name("PTR_GIRDLE_GUIDE_1"))
        self.assertFalse(is_rehearsal_metal_name("PTR_NOTES"))

    def test_script_copies_before_boolean_and_preserves_inputs(self) -> None:
        script = build_metal_union_rehearsal_script(Path("C:/Memory/report.json"))
        compile(script, "metal_union_rehearsal.py", "exec")

        self.assertLess(script.index("rs.CopyObjects(source_ids)"), script.index("rs.BooleanUnion(copy_ids"))
        self.assertIn("delete_input=False", script)
        self.assertNotIn("rs.BooleanUnion(source_ids", script)
        self.assertNotIn("rs.DeleteObject", script)
        self.assertNotIn("rs.MoveObject", script)
        self.assertNotIn("rs.Command", script)
        self.assertIn('"original_geometry_modified": False', script)
        self.assertIn('"production_export_allowed": False', script)

    def test_script_requires_one_clean_closed_result(self) -> None:
        script = build_metal_union_rehearsal_script(Path("C:/Memory/report.json"))
        self.assertIn("len(result_ids) == 1", script)
        self.assertIn("rs.IsObjectSolid(result_ids[0])", script)
        self.assertIn('report["result_naked_edges"] == 0', script)
        self.assertIn("METAL_UNION_REHEARSAL_PASSED", script)
        self.assertIn("METAL_UNION_REHEARSAL_BLOCKED", script)

    def test_prepare_and_save_uses_rehearsal_memory_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_root = Path(temp_dir)
            now = datetime(2026, 7, 17, 19, 30, 0, 123456)
            script_path, report_path, script = prepare_metal_union_rehearsal(
                memory_root,
                now,
            )
            self.assertEqual(script_path.parent, memory_root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, memory_root / "Metal_Union_Rehearsals")
            self.assertIn("2026-07-17_19-30-00-123456", script_path.name)
            save_metal_union_rehearsal(script_path, script)
            self.assertTrue(script_path.exists())
            self.assertIn("ptr-metal-union-rehearsal-v1", script_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
