"""Tests for Bridge Boolean Rehearsal."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from utils.bridge_boolean_rehearsal_generator import (
    build_bridge_boolean_rehearsal_script,
    prepare_bridge_boolean_rehearsal,
    rehearsal_status,
    save_bridge_boolean_rehearsal,
)


class BridgeBooleanRehearsalTests(unittest.TestCase):
    def test_statuses(self):
        self.assertEqual(rehearsal_status(0, False, -1), "BOOLEAN_RESULT_COUNT_INVALID")
        self.assertEqual(rehearsal_status(2, True, 0), "BOOLEAN_RESULT_COUNT_INVALID")
        self.assertEqual(rehearsal_status(1, False, 0), "BOOLEAN_RESULT_NOT_CLOSED")
        self.assertEqual(rehearsal_status(1, True, 1), "BOOLEAN_RESULT_HAS_NAKED_EDGES")
        self.assertEqual(rehearsal_status(1, True, 0), "BRIDGE_BOOLEAN_REHEARSAL_PASSED")

    def test_script_copies_before_union_and_preserves_inputs(self):
        script = build_bridge_boolean_rehearsal_script(Path("bridge_boolean.json"))
        compile(script, "bridge_boolean_rehearsal.py", "exec")
        self.assertIn("rs.CopyObject", script)
        self.assertIn("rs.BooleanUnion(copy_ids, delete_input=False)", script)
        self.assertLess(script.index("rs.CopyObject"), script.index("rs.BooleanUnion"))
        for forbidden in ("rs.Delete", "rs.Move", "rs.Save", "rs.Export"):
            self.assertNotIn(forbidden, script)
        self.assertIn("BOOLEAN USED ORIGINAL IDS | NO", script)
        self.assertIn("PRODUCTION EXPORT | BLOCKED", script)

    def test_prepare_and_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            script_path, report_path, script = prepare_bridge_boolean_rehearsal(
                root, datetime(2026, 7, 18, 18, 15, 0)
            )
            self.assertEqual(script_path.parent, root / "Rhino_Scripts")
            self.assertEqual(report_path.parent, root / "Bridge_Boolean_Rehearsals")
            save_bridge_boolean_rehearsal(script_path, script)
            self.assertTrue(script_path.exists())


if __name__ == "__main__":
    unittest.main()
