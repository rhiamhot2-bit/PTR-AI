import unittest

from utils.cad_rules import validate_cad_request
from utils.rhino_setting_v3_generator import build_rhino_setting_v3_script


SAFE = (
    "แหวนไซซ์ 52 ทอง 18K มรกต Oval 8x6 มม. หนามเตย 4 เตย "
    "ก้านกว้าง 2.5 มม. ก้านหนา 1.8 มม. หนามเตยหนา 0.7 มม. "
    "ระยะเผื่อฝัง 0.1 มม. หัวแหวนสูง 6.5 มม."
)


class RhinoSettingV3Tests(unittest.TestCase):
    def test_v3_adds_guides_inward_prongs_and_audit(self) -> None:
        script = build_rhino_setting_v3_script(validate_cad_request(SAFE))
        self.assertIn("ptr-rhino-setting-v3", script)
        self.assertIn("PTR_GIRDLE_GUIDE_", script)
        self.assertIn("x * 0.88", script)
        self.assertIn("geometry_audit", script)
        self.assertIn("manual Boolean required", script)
        self.assertIn("rs.RotateObjects(created, (0, 0, 0), 90.0, (1, 0, 0), False)", script)
        self.assertIn("rs.RotateObjects(head_objects, (0, 0, 0), 90.0, (0, 0, 1), False)", script)
        self.assertIn("PTR_SETTING_CONCEPT", script)

    def test_v3_keeps_four_prong_base(self) -> None:
        script = build_rhino_setting_v3_script(validate_cad_request(SAFE))
        self.assertIn("prong_points = [", script)
        self.assertIn("PTR_PRONG_", script)

    def test_v3_rejects_unsafe_input(self) -> None:
        with self.assertRaises(ValueError):
            build_rhino_setting_v3_script(validate_cad_request("แหวนทอง 18K มรกต"))


if __name__ == "__main__":
    unittest.main()
