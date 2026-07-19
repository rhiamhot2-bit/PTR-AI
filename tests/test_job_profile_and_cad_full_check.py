import tempfile
import unittest
from pathlib import Path
from utils.job_profile import normalized_profile, parse_profile_arguments, save_profile, load_profile, validate_profile
from utils.cad_full_check_generator import build_cad_full_check_script, full_check_status
from commands.cadfullcheck import parse_full_check_arguments

VALUES={"prong_count":4,"prong_angle_deg":11.0,"prong_diameter_mm":1.0,"prong_engagement_ratio":0.25,"prong_trim_allowance_mm":0.8,"support_count":2,"support_style":"CURVED","support_diameter_mm":0.9,"support_top_overlap_mm":0.2,"support_bottom_overlap_mm":0.2,"minimum_member_mm":0.8,"angle_tolerance_deg":0.25,"symmetry_tolerance_mm":0.25,"contact_tolerance_mm":0.01}

class JobProfileAndFullCheckTests(unittest.TestCase):
    def test_profile_is_complete_and_parameterized(self):
        self.assertEqual(validate_profile(VALUES),[])
        self.assertEqual(validate_profile(dict(VALUES,prong_angle_deg=0,support_style="STRAIGHT")),[])
        self.assertEqual(validate_profile(dict(VALUES,prong_angle_deg=15,support_style="CUSTOM")),[])
    def test_parser_rejects_unknowns(self):
        values,errors=parse_profile_arguments(("prong_angle_deg=15","unknown=1"))
        self.assertEqual(values["prong_angle_deg"],15.0); self.assertTrue(errors)
    def test_full_check_options_are_not_profile_fields(self):
        tokens,options,errors=parse_full_check_arguments(("source=LATEST_EDITABLE","source_layer=PTR_PARTS","prong_angle_deg=15"))
        self.assertEqual(tokens,["prong_angle_deg=15"])
        self.assertEqual(options["source_layer"],"PTR_PARTS")
        self.assertEqual(errors,[])
    def test_save_load(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"profile.json"; save_profile(p,VALUES)
            self.assertEqual(load_profile(p)["assembly_mode"],"EDITABLE_NON_UNION")
    def test_script_is_report_only_and_source_aware(self):
        script=build_cad_full_check_script(Path("report.json"),normalized_profile(VALUES),{"source":"LATEST_EDITABLE","source_layer":""})
        compile(script,"fullcheck.py","exec")
        self.assertIn('"prong_angle_deg": 11.0',script)
        self.assertIn("SOURCE OPTIONS",script)
        self.assertIn("FULL_CHECK_BLOCKED_AMBIGUOUS_SOURCE",script)
        self.assertIn("SOURCE GEOMETRY MODIFIED | NO",script)
        for forbidden in ("rs.Delete","rs.Move","rs.Rotate","AddBrep","CreateBooleanUnion"):
            self.assertNotIn(forbidden,script)
    def test_status(self):
        self.assertEqual(full_check_status(True,True,True,True,True,True),"EDITABLE_ASSEMBLY_READY")
        self.assertEqual(full_check_status(False,True,True,True,True,True),"JOB_PROFILE_REQUIRED")
if __name__=="__main__": unittest.main()
