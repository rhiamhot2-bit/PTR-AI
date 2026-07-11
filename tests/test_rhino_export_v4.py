import tempfile
import unittest
from pathlib import Path

from utils.cad_rules import validate_cad_request
from utils.rhino_export_v4_generator import (
    build_rhino_export_v4_script,
    prepare_v4_paths,
)


SAFE = (
    "แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย "
    "ก้านกว้าง 2.5 มม. ก้านหนา 1.8 มม. หนามเตยหนา 0.7 มม. "
    "ระยะเผื่อฝัง 0.1 มม. หัวแหวนสูง 6.5 มม."
)


class RhinoExportV4Tests(unittest.TestCase):
    def test_v4_contains_naked_edge_audit_and_guarded_save(self) -> None:
        report = validate_cad_request(SAFE)
        script = build_rhino_export_v4_script(
            report,
            Path("C:/PTR/ring.3dm"),
            Path("C:/PTR/audit.json"),
        )
        self.assertIn("DuplicateNakedEdgeCurves", script)
        self.assertIn("can_export_3dm", script)
        self.assertIn("V4 EXPORT BLOCKED", script)
        self.assertIn("_-SaveAs", script)
        self.assertIn("ptr-rhino-export-v4", script)

    def test_unique_v4_paths_use_separate_folders(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            script, model, audit = prepare_v4_paths(Path(temp))
            self.assertEqual(script.suffix, ".py")
            self.assertEqual(model.suffix, ".3dm")
            self.assertEqual(audit.suffix, ".json")
            self.assertNotEqual(script.parent, model.parent)
            self.assertNotEqual(model.parent, audit.parent)

    def test_v4_rejects_unsafe_input(self) -> None:
        report = validate_cad_request("แหวนทอง 18K มรกต")
        with self.assertRaises(ValueError):
            build_rhino_export_v4_script(
                report,
                Path("ring.3dm"),
                Path("audit.json"),
            )


if __name__ == "__main__":
    unittest.main()
