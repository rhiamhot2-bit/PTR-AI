import math
import tempfile
import unittest
from pathlib import Path

from utils.cad_rules import validate_cad_request
from utils.rhino_script_generator import (
    build_rhino_ring_script,
    ring_inner_diameter_mm,
    save_rhino_script,
)


SAFE_REQUEST = (
    "แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย "
    "ก้านกว้าง 2.5 มม. ก้านหนา 1.8 มม. หนามเตยหนา 0.7 มม. "
    "ระยะเผื่อฝัง 0.1 มม. หัวแหวนสูง 6.5 มม."
)


class RhinoScriptGeneratorTests(unittest.TestCase):
    def test_eu_size_converts_to_inner_diameter(self) -> None:
        self.assertAlmostEqual(ring_inner_diameter_mm(52), 52 / math.pi)

    def test_ready_report_generates_reviewable_rhino_script(self) -> None:
        report = validate_cad_request(SAFE_REQUEST)
        script = build_rhino_ring_script(report)
        self.assertIn("rs.AddTorus", script)
        self.assertIn("rs.AddSphere", script)
        self.assertIn("professional review required", script.lower())
        self.assertIn("PTR_RING_BAND_SIZE_52", script)

    def test_non_ready_report_is_rejected(self) -> None:
        report = validate_cad_request("แหวนทอง 18K มรกต")
        with self.assertRaises(ValueError):
            build_rhino_ring_script(report)

    def test_script_is_saved_as_utf8_python_file(self) -> None:
        report = validate_cad_request(SAFE_REQUEST)
        script = build_rhino_ring_script(report)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(save_rhino_script(Path(temp_dir), report, script))
            self.assertTrue(path.exists())
            self.assertEqual(path.suffix, ".py")
            self.assertEqual(path.read_text(encoding="utf-8"), script)


if __name__ == "__main__":
    unittest.main()
