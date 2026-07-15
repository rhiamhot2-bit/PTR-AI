"""Build a contact-audited Shoulder Loft v4 Rhino review script."""

from datetime import datetime
from pathlib import Path

from utils.shoulder_geometry_generator import build_shoulder_geometry_script


GENERATOR_VERSION = "ptr-shoulder-loft-v4-contact-audit"


def prepare_shoulder_loft_v4_paths(memory_root: Path):
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    report_dir = memory_root / "Shoulder_Loft_v4"
    script_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    return (
        script_dir / f"{stamp}_shoulder_loft_v4.py",
        report_dir / f"{stamp}_shoulder_loft_v4.json",
    )


def build_shoulder_loft_v4_script(output_report: Path) -> str:
    """Extend the existing five-section loft with a real Brep contact audit."""

    base_script = build_shoulder_geometry_script(output_report)
    audit_script = r'''

# Shoulder Loft v4 contact audit. This block runs after the review geometry is built.
CONTACT_AUDIT_VERSION = "ptr-shoulder-contact-audit-v1"
CONTACT_SHOULDER_NAMES = ("PTR_SHOULDER_LEFT", "PTR_SHOULDER_RIGHT")
CONTACT_SETTING_MARKERS = ("STONE_SEAT", "BASKET_SUPPORT")


def ptr_object_brep(obj_id):
    rhino_object = sc.doc.Objects.Find(obj_id)
    if not rhino_object:
        return None
    geometry = rhino_object.Geometry
    if isinstance(geometry, Rhino.Geometry.Brep):
        return geometry
    return geometry.ToBrep() if hasattr(geometry, "ToBrep") else None


def ptr_brep_intersects(first_brep, second_brep, tolerance):
    if first_brep is None or second_brep is None:
        return False
    result = Rhino.Geometry.Intersect.Intersection.BrepBrep(
        first_brep, second_brep, tolerance
    )
    if not result:
        return False

    success = True
    curves = []
    points = []
    if isinstance(result, tuple):
        if len(result) == 3:
            success, curves, points = result
        elif len(result) == 2:
            curves, points = result
    return bool(
        success
        and (
            (curves is not None and len(curves) > 0)
            or (points is not None and len(points) > 0)
        )
    )


def ptr_run_contact_audit():
    band = None
    settings = []
    shoulders = {}

    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or ""
        upper = name.upper()
        entry = {"id": obj_id, "name": name, "brep": ptr_object_brep(obj_id)}
        if "RING_BAND" in upper:
            band = entry
        if any(marker in upper for marker in CONTACT_SETTING_MARKERS):
            settings.append(entry)
        if name in CONTACT_SHOULDER_NAMES:
            shoulders[name] = entry

    tolerance = max(float(sc.doc.ModelAbsoluteTolerance), 0.001)
    checks = []
    for shoulder_name in CONTACT_SHOULDER_NAMES:
        shoulder = shoulders.get(shoulder_name)
        shoulder_brep = shoulder["brep"] if shoulder else None
        band_contact = ptr_brep_intersects(
            shoulder_brep, band["brep"] if band else None, tolerance
        )
        setting_hits = [
            setting["name"]
            for setting in settings
            if ptr_brep_intersects(shoulder_brep, setting["brep"], tolerance)
        ]
        checks.append(
            {
                "shoulder": shoulder_name,
                "exists": shoulder is not None,
                "closed_solid": bool(
                    shoulder_brep is not None and shoulder_brep.IsSolid
                ),
                "band_surface_intersection": band_contact,
                "setting_surface_intersections": setting_hits,
                "contact_verified": bool(band_contact and setting_hits),
            }
        )

    all_verified = len(checks) == 2 and all(
        item["contact_verified"] for item in checks
    )
    try:
        with io.open(OUTPUT_REPORT, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        payload = {}

    payload["contact_audit_version"] = CONTACT_AUDIT_VERSION
    payload["contact_tolerance_mm"] = tolerance
    payload["contact_checks"] = checks
    payload["all_contacts_verified"] = all_verified
    payload["production_export_allowed"] = False
    payload["status"] = (
        "SHOULDER_LOFT_V4_CONTACT_REVIEW_REQUIRED"
        if all_verified
        else "SHOULDER_LOFT_V4_CONTACT_BLOCKED"
    )

    with io.open(OUTPUT_REPORT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    for item in checks:
        print(
            "SHOULDER CONTACT | {0} | band={1} | setting={2} | verified={3}".format(
                item["shoulder"],
                item["band_surface_intersection"],
                len(item["setting_surface_intersections"]),
                item["contact_verified"],
            )
        )
    print("SHOULDER CONTACT OVERALL | verified={0}".format(all_verified))
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")


ptr_run_contact_audit()
'''
    return base_script + audit_script


def save_shoulder_loft_v4_script(script: str, script_path: Path) -> Path:
    script_path.write_text(script, encoding="utf-8")
    return script_path
