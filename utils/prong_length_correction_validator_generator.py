"""Generate a report-only Prong Length Correction Validator."""

from datetime import datetime
import json
from pathlib import Path


def correction_validation_status(count, all_ready):
    if count != 4:
        return "PRONG_LENGTH_CORRECTION_VALIDATION_BLOCKED_COUNT"
    return "PRONG_LENGTH_CORRECTION_VALIDATION_READY" if all_ready else "PRONG_LENGTH_CORRECTION_VALIDATION_REVIEW_REQUIRED"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Prong Length Correction Validator
# REPORT ONLY: never moves, adds, deletes, Booleans, or exports geometry.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
TARGET_ALLOWANCE_MM = 0.80
ALLOWANCE_TOLERANCE_MM = 0.01
TARGET_TILT_DEG = 11.0
TILT_TOLERANCE_DEG = 0.25
MAX_BASE_SHIFT_MM = 0.02
MAX_DIAMETER_CHANGE_MM = 0.03
MAX_ALLOWANCE_SPREAD_MM = 0.01
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj = sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None


def bounds(object_id):
    box = rs.BoundingBox(object_id)
    if not box:
        return None
    xs = [p.X for p in box]
    ys = [p.Y for p in box]
    zs = [p.Z for p in box]
    return {
        "min_z": min(zs), "max_z": max(zs),
        "center": Rhino.Geometry.Point3d(
            (min(xs) + max(xs)) / 2.0,
            (min(ys) + max(ys)) / 2.0,
            (min(zs) + max(zs)) / 2.0,
        ),
    }


def intersects(first, second):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(
            first, second, MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def volume_of(brep):
    try:
        properties = Rhino.Geometry.VolumeMassProperties.Compute(brep)
        return properties.Volume if properties else 0.0
    except Exception:
        return 0.0


def principal_measurements(brep):
    meshes = Rhino.Geometry.Mesh.CreateFromBrep(brep, Rhino.Geometry.MeshingParameters.FastRenderMesh)
    points = []
    for mesh in meshes or []:
        for vertex in mesh.Vertices:
            points.append(Rhino.Geometry.Point3d(vertex.X, vertex.Y, vertex.Z))
    if len(points) < 4:
        return None
    center = Rhino.Geometry.Point3d(
        sum(p.X for p in points) / len(points),
        sum(p.Y for p in points) / len(points),
        sum(p.Z for p in points) / len(points),
    )
    covariance = [[0.0, 0.0, 0.0] for _ in range(3)]
    for point in points:
        values = [point.X - center.X, point.Y - center.Y, point.Z - center.Z]
        for row in range(3):
            for column in range(3):
                covariance[row][column] += values[row] * values[column]
    vector = [0.1, 0.1, 1.0]
    for _ in range(30):
        next_vector = [
            sum(covariance[row][column] * vector[column] for column in range(3))
            for row in range(3)
        ]
        magnitude = math.sqrt(sum(value * value for value in next_vector))
        if magnitude <= 0:
            return None
        vector = [value / magnitude for value in next_vector]
    axis = Rhino.Geometry.Vector3d(vector[0], vector[1], vector[2])
    if axis.Z < 0:
        axis.Reverse()
    projections = [
        (point.X - center.X) * axis.X
        + (point.Y - center.Y) * axis.Y
        + (point.Z - center.Z) * axis.Z
        for point in points
    ]
    minimum = min(projections)
    maximum = max(projections)
    length = maximum - minimum
    base = center + axis * minimum
    volume = volume_of(brep)
    diameter = 2.0 * math.sqrt(volume / (math.pi * length)) if volume > 0 and length > 0 else 0.0
    tilt = math.degrees(math.acos(max(-1.0, min(1.0, axis.Z))))
    return {"axis": axis, "base": base, "length": length, "diameter": diameter, "tilt": tilt}


def main():
    sources = {}
    corrected = []
    stone_id = None
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        upper = object_name(object_id).upper()
        if upper.endswith("_LENGTH_CORRECTION_TRIAL"):
            corrected.append(object_id)
        elif upper.startswith("PTR_PRONG_") and "11DEG_REPOSITION_COPY" in upper:
            sources[upper] = object_id
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper
            and not any(word in upper for word in ("TRIAL", "COPY", "REHEARSAL", "RESULT"))
        ):
            stone_id = object_id

    stone_box = bounds(stone_id) if stone_id else None
    stone_brep = brep_for(stone_id) if stone_id else None
    blockers = []
    if len(corrected) != 4:
        blockers.append("Exactly four corrected trial prongs are required.")
    if stone_box is None or stone_brep is None:
        blockers.append("Stone Placeholder is required.")

    rows = []
    allowances = []
    for corrected_id in sorted(corrected, key=object_name):
        corrected_name = object_name(corrected_id)
        source_name = corrected_name.upper().replace("_LENGTH_CORRECTION_TRIAL", "")
        source_id = sources.get(source_name)
        corrected_brep = brep_for(corrected_id)
        source_brep = brep_for(source_id) if source_id else None
        corrected_measure = principal_measurements(corrected_brep) if corrected_brep else None
        source_measure = principal_measurements(source_brep) if source_brep else None
        box = bounds(corrected_id)
        allowance = box["max_z"] - stone_box["max_z"] if box and stone_box else None
        if allowance is not None:
            allowances.append(allowance)
        base_shift = (
            corrected_measure["base"].DistanceTo(source_measure["base"])
            if corrected_measure and source_measure else None
        )
        diameter_change = (
            abs(corrected_measure["diameter"] - source_measure["diameter"])
            if corrected_measure and source_measure else None
        )
        radial = Rhino.Geometry.Vector3d(
            corrected_measure["base"].X - stone_box["center"].X,
            corrected_measure["base"].Y - stone_box["center"].Y,
            0.0,
        ) if corrected_measure and stone_box else None
        outward = bool(
            radial and radial.Unitize()
            and corrected_measure["axis"].X * radial.X + corrected_measure["axis"].Y * radial.Y > 0
        )
        stone_collision = intersects(corrected_brep, stone_brep) if corrected_brep and stone_brep else True
        checks = {
            "allowance_ready": allowance is not None and abs(allowance - TARGET_ALLOWANCE_MM) <= ALLOWANCE_TOLERANCE_MM,
            "tilt_ready": corrected_measure is not None and abs(corrected_measure["tilt"] - TARGET_TILT_DEG) <= TILT_TOLERANCE_DEG,
            "outward": outward,
            "base_ready": base_shift is not None and base_shift <= MAX_BASE_SHIFT_MM,
            "diameter_ready": diameter_change is not None and diameter_change <= MAX_DIAMETER_CHANGE_MM,
            "stone_clear": not stone_collision,
        }
        rows.append({
            "name": corrected_name,
            "source_found": source_id is not None,
            "allowance_mm": round(allowance, 3) if allowance is not None else None,
            "tilt_deg": round(corrected_measure["tilt"], 3) if corrected_measure else None,
            "outward": outward,
            "base_shift_mm": round(base_shift, 4) if base_shift is not None else None,
            "diameter_mm": round(corrected_measure["diameter"], 3) if corrected_measure else None,
            "diameter_change_mm": round(diameter_change, 4) if diameter_change is not None else None,
            "stone_collision": stone_collision,
            "checks": checks,
            "ready": all(checks.values()),
        })

    spread = max(allowances) - min(allowances) if allowances else None
    symmetry_ready = spread is not None and spread <= MAX_ALLOWANCE_SPREAD_MM
    all_ready = len(rows) == 4 and symmetry_ready and all(row["ready"] for row in rows)
    status = (
        "PRONG_LENGTH_CORRECTION_VALIDATION_READY"
        if all_ready and not blockers
        else "PRONG_LENGTH_CORRECTION_VALIDATION_REVIEW_REQUIRED"
    )
    if len(corrected) != 4:
        status = "PRONG_LENGTH_CORRECTION_VALIDATION_BLOCKED_COUNT"

    report = {
        "generator": "ptr-prong-length-correction-validator-v1",
        "status": status,
        "corrected_count": len(corrected),
        "ready_count": sum(1 for row in rows if row["ready"]),
        "allowance_spread_mm": round(spread, 4) if spread is not None else None,
        "symmetry_ready": symmetry_ready,
        "prongs": rows,
        "blockers": blockers,
        "geometry_modified": False,
        "temporary_geometry_added": False,
        "boolean_executed": False,
        "production_export_allowed": False,
    }
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("PRONG LENGTH CORRECTION VALIDATOR | status=" + status)
    print("CORRECTED PRONGS | count={0} | ready={1}".format(
        len(corrected), sum(1 for row in rows if row["ready"])
    ))
    for row in rows:
        print("PRONG CORRECTION CHECK | {0} | ready={1} | allowance_mm={2} | tilt_deg={3} | outward={4} | base_shift_mm={5} | diameter_mm={6} | diameter_change_mm={7} | stone_collision={8}".format(
            row["name"], row["ready"], row["allowance_mm"], row["tilt_deg"],
            row["outward"], row["base_shift_mm"], row["diameter_mm"],
            row["diameter_change_mm"], row["stone_collision"]
        ))
    print("CORRECTION SYMMETRY | spread_mm={0} | ready={1}".format(
        round(spread, 4) if spread is not None else None, symmetry_ready
    ))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("TEMPORARY GEOMETRY ADDED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PRONG CORRECTION VALIDATION REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_prong_length_correction_validator_script(report_path):
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/"))
    )


def prepare_prong_length_correction_validator(memory_root, now=None):
    stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_prong_length_correction_validator.py"
    report_path = memory_root / "Prong_Length_Correction_Validation" / f"{stamp}_prong_length_correction_validator.json"
    return script_path, report_path, build_prong_length_correction_validator_script(report_path)


def save_prong_length_correction_validator(script_path, script):
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
