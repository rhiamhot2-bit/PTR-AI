import tempfile
import unittest
from pathlib import Path

from utils.cad_rules import validate_cad_request
from utils.rhino_setting_v2_generator import (
    build_rhino_setting_v2_script,
    save_rhino_setting_v2_script,
)


SAFE = (
    "แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย "
    "ก้านกว้าง 2.5 มม. ก้านหนา 1.8 มม. หนามเตยหนา 0.7 มม. "
    "ระยะเผื่อฝัง 0.1 มม. หัวแหวนสูง 6.5 มม."
)


class RhinoSettingV2Tests(unittest.TestCase):
    def test_script_contains_seat_four_prongs_and_supports(self) -> None:
        script = build_rhino_setting_v2_script(validate_cad_request(SAFE))
        self.assertIn("rs.AddEllipse", script)
        self.assertIn("rs.AddPipe", script)
        self.assertIn("PTR_PRONG_", script)
        self.assertIn("PTR_BASKET_SUPPORT_", script)

    def test_unsafe_request_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_rhino_setting_v2_script(validate_cad_request("แหวนทอง 18K มรกต"))

    def test_v2_script_saves(self) -> None:
        script = build_rhino_setting_v2_script(validate_cad_request(SAFE))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(save_rhino_setting_v2_script(Path(temp), script))
            self.assertTrue(path.name.endswith("_setting_v2.py"))


if __name__ == "__main__":
    unittest.main()
