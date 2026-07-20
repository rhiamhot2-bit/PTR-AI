"""Generate a report-only Rhino 8 validator for a corrected stone-seat trial."""

from datetime import datetime
from pathlib import Path
import json


TRIAL_NAME = "PTR_OVAL_STONE_SEAT_THICKNESS_CORRECTION_TRIAL"
DEFAULT_MINIMUM_MEMBER_MM = 0.8


def _target_from_profile(memory_root):
    profile_path = Path(memory_root) / "Job_Profiles" / "current.json"
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        return float(profile.get("minimum_member_mm", DEFAULT_MINIMUM_MEMBER_MM))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_MINIMUM_MEMBER_MM


def prepare_seat_thickness_correction_validator(memory_root):
    memory_root = Path(memory_root)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_seat_thickness_correction_validator.py"
    report_path = memory_root / "Seat_Thickness_Correction_Validation" / f"{stamp}_seat_thickness_correction_validator.json"
    target = _target_from_profile(memory_root)
    script = _render_script(report_path.as_posix(), target)
    return script_path, report_path, script


def save_seat_thickness_correction_validator(script_path, script):
    script_path = Path(script_path)
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")


def _render_script(report_path, target_mm):
    return f'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Seat Thickness Correction Validator
# REPORT ONLY: never moves, deletes, joins, Booleans, or exports geometry.
import io
import json
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

TRIAL_NAME = {TRIAL_NAME!r}
TARGET_MM = {target_mm!r}
REPORT_PATH = {report_path!r}


def write_report(payload):
    folder = __import__("os").path.dirname(REPORT_PATH)
    if folder and not __import__("os").path.isdir(folder):
        __import__("os").makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)


def main():
    matches = [object_id for object_id in rs.AllObjects() if (rs.ObjectName(object_id) or "") == TRIAL_NAME]
    if len(matches) != 1:
        status = "SEAT_THICKNESS_CORRECTION_VALIDATION_SOURCE_NOT_UNIQUE"
        print("SEAT THICKNESS CORRECTION VALIDATOR | status=" + status)
        print("TRIAL COUNT | count=" + str(len(matches)))
        write_report({{"status": status, "trial_count": len(matches), "geometry_modified": False}})
        return

    obj = sc.doc.Objects.Find(matches[0])
    brep = obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None
    if brep is None:
        status = "SEAT_THICKNESS_CORRECTION_VALIDATION_NOT_BREP"
        print("SEAT THICKNESS CORRECTION VALIDATOR | status=" + status)
        write_report({{"status": status, "geometry_modified": False}})
        return

    bbox = brep.GetBoundingBox(True)
    measured = min(bbox.Max.X-bbox.Min.X, bbox.Max.Y-bbox.Min.Y, bbox.Max.Z-bbox.Min.Z)
    closed = bool(brep.IsSolid)
    naked_edges = len(brep.DuplicateNakedEdgeCurves(True, True))
    ready = closed and naked_edges == 0 and measured + sc.doc.ModelAbsoluteTolerance >= TARGET_MM
    status = "SEAT_THICKNESS_CORRECTION_VALIDATION_READY" if ready else "SEAT_THICKNESS_CORRECTION_VALIDATION_REVIEW_REQUIRED"
    print("SEAT THICKNESS CORRECTION VALIDATOR | status=" + status)
    print("SEAT CHECK | " + TRIAL_NAME + " | ready=" + str(ready) + " | measured_mm=" + format(measured, ".3f") + " | required_mm=" + format(TARGET_MM, ".3f") + " | closed=" + str(closed) + " | naked_edges=" + str(naked_edges))
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    write_report({{"status": status, "trial": TRIAL_NAME, "ready": ready, "measured_mm": measured, "required_mm": TARGET_MM, "closed": closed, "naked_edges": naked_edges, "geometry_modified": False, "boolean_executed": False, "production_export": "BLOCKED"}})


if __name__ == "__main__":
    main()
'''
