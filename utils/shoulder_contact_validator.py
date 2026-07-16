from __future__ import annotations

from datetime import datetime
from pathlib import Path

GENERATOR_VERSION = "ptr-shoulder-contact-validator-v1"


def build_shoulder_contact_validator_script(output_path: Path) -> str:
    report_path = str(output_path).replace("\\", "/")
    return f'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Shoulder Contact Validator
# Generator: {GENERATOR_VERSION}
# REPORT ONLY: never creates, joins, deletes, moves, renames, or exports geometry.
import io
import json
import math
import os

import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_PATH = r"{report_path}"
CONTACT_TOLERANCE_MM = 0.05
SYMMETRY_TOLERANCE_MM = 0.15

REQUIRED_OBJECTS = [
    "PTR_SHOULDER_LEFT",
    "PTR_SHOULDER_RIGHT",
    "PTR_RING_BAND_SIZE_52",
    "PTR_OVAL_STONE_SEAT_CONCEPT",
]


def find_named(name):
    matches = []
    for object_id in rs.AllObjects() or []:
        if (rs.ObjectName(object_id) or "").upper() == name:
            matches.append(object_id)
    return matches


def to_brep(object_id):
    rhino_object = sc.doc.Objects.FindId(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    if isinstance(geometry, Rhino.Geometry.Brep):
        return geometry
    return Rhino.Geometry.Brep.TryConvertBrep(geometry)


def box_values(brep):
    box = brep.GetBoundingBox(True)
    minimum = box.Min
    maximum = box.Max
    return {{
        "min": [minimum.X, minimum.Y, minimum.Z],
        "max": [maximum.X, maximum.Y, maximum.Z],
        "center": [
            (minimum.X + maximum.X) / 2.0,
            (minimum.Y + maximum.Y) / 2.0,
            (minimum.Z + maximum.Z) / 2.0,
        ],
        "size": [maximum.X - minimum.X, maximum.Y - minimum.Y, maximum.Z - minimum.Z],
    }}


def bbox_gap(first, second):
    squared = 0.0
    for axis in range(3):
        if first["max"][axis] < second["min"][axis]:
            distance = second["min"][axis] - first["max"][axis]
        elif second["max"][axis] < first["min"][axis]:
            distance = first["min"][axis] - second["max"][axis]
        else:
            distance = 0.0
        squared += distance * distance
    return math.sqrt(squared)


def audit_named(name):
    matches = find_named(name)
    result = {{"name": name, "count": len(matches), "exists": bool(matches)}}
    if len(matches) != 1:
        result["passed"] = False
        result["reason"] = "expected exactly one named object"
        return result

    brep = to_brep(matches[0])
    if brep is None:
        result["passed"] = False
        result["reason"] = "object cannot be converted to Brep"
        return result

    result["closed"] = bool(brep.IsSolid)
    result["bbox"] = box_values(brep)
    result["passed"] = bool(brep.IsSolid)
    if not result["passed"]:
        result["reason"] = "object is not a closed solid"
    return result


def contact_result(shoulder, target, label):
    gap = bbox_gap(shoulder["bbox"], target["bbox"])
    return {{
        "label": label,
        "bbox_gap_mm": round(gap, 6),
        "tolerance_mm": CONTACT_TOLERANCE_MM,
        "contact_candidate": gap <= CONTACT_TOLERANCE_MM,
        "method": "conservative bounding-box proximity; professional review required",
    }}


def symmetry_result(left, right, seat):
    left_box = left["bbox"]
    right_box = right["bbox"]
    seat_x = seat["bbox"]["center"][0]
    size_delta = [abs(left_box["size"][i] - right_box["size"][i]) for i in range(3)]
    mirror_x_delta = abs((left_box["center"][0] + right_box["center"][0]) - (2.0 * seat_x))
    yz_delta = [
        abs(left_box["center"][1] - right_box["center"][1]),
        abs(left_box["center"][2] - right_box["center"][2]),
    ]
    maximum_delta = max(size_delta + [mirror_x_delta] + yz_delta)
    return {{
        "size_delta_mm": [round(value, 6) for value in size_delta],
        "mirror_x_delta_mm": round(mirror_x_delta, 6),
        "yz_center_delta_mm": [round(value, 6) for value in yz_delta],
        "maximum_delta_mm": round(maximum_delta, 6),
        "tolerance_mm": SYMMETRY_TOLERANCE_MM,
        "passed": maximum_delta <= SYMMETRY_TOLERANCE_MM,
    }}


def main():
    audited = {{name: audit_named(name) for name in REQUIRED_OBJECTS}}
    blockers = []
    warnings = [
        "Contact is inferred from bounding-box proximity, not proven by Boolean intersection.",
        "A jewelry CAD professional must inspect shoulder thickness, fillets, casting flow, and polishing allowance.",
    ]

    for name in REQUIRED_OBJECTS:
        if not audited[name].get("passed"):
            blockers.append(name + ": " + audited[name].get("reason", "audit failed"))

    contacts = []
    symmetry = None
    if not blockers:
        left = audited["PTR_SHOULDER_LEFT"]
        right = audited["PTR_SHOULDER_RIGHT"]
        band = audited["PTR_RING_BAND_SIZE_52"]
        seat = audited["PTR_OVAL_STONE_SEAT_CONCEPT"]
        contacts = [
            contact_result(left, band, "left shoulder to ring band"),
            contact_result(left, seat, "left shoulder to stone seat"),
            contact_result(right, band, "right shoulder to ring band"),
            contact_result(right, seat, "right shoulder to stone seat"),
        ]
        for contact in contacts:
            if not contact["contact_candidate"]:
                blockers.append(contact["label"] + ": no contact candidate within tolerance")

        symmetry = symmetry_result(left, right, seat)
        if not symmetry["passed"]:
            blockers.append("left/right shoulder symmetry exceeds tolerance")

    status = "SHOULDER_CONTACT_BLOCKED" if blockers else "SHOULDER_CONTACT_REVIEW_REQUIRED"
    report = {{
        "generator": "{GENERATOR_VERSION}",
        "status": status,
        "units": "millimeters",
        "contact_tolerance_mm": CONTACT_TOLERANCE_MM,
        "symmetry_tolerance_mm": SYMMETRY_TOLERANCE_MM,
        "objects": audited,
        "contacts": contacts,
        "symmetry": symmetry,
        "blockers": blockers,
        "warnings": warnings,
        "production_export_allowed": False,
        "geometry_modified": False,
    }}

    folder = os.path.dirname(OUTPUT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("SHOULDER CONTACT AUDIT | status=" + status)
    for contact in contacts:
        print("CONTACT | {{0}} | gap_mm={{1}} | candidate={{2}}".format(
            contact["label"], contact["bbox_gap_mm"], contact["contact_candidate"]
        ))
    if symmetry is not None:
        print("SYMMETRY | max_delta_mm={{0}} | passed={{1}}".format(
            symmetry["maximum_delta_mm"], symmetry["passed"]
        ))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("PRODUCTION EXPORT | BLOCKED")
    print("AUDIT JSON | " + OUTPUT_PATH)
    print("No geometry was modified.")


if __name__ == "__main__":
    main()
'''


def prepare_shoulder_contact_validator(memory_root: Path) -> tuple[Path, Path, str]:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_shoulder_contact_check.py"
    report_path = memory_root / "Shoulder_Contact_Audits" / f"{timestamp}_shoulder_contact.json"
    script = build_shoulder_contact_validator_script(report_path)
    return script_path, report_path, script


def save_shoulder_contact_validator(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
