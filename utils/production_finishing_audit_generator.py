"""Generate a report-only Rhino Production Finishing Audit."""

from datetime import datetime
import json
from pathlib import Path


def finishing_status(candidate_count, prong_count, support_count, closed, naked_edges, stone_collision):
    if candidate_count != 1:
        return "FINISHING_AUDIT_BLOCKED_CANDIDATE"
    if prong_count != 4 or support_count != 2:
        return "FINISHING_AUDIT_BLOCKED_MEMBER_COUNT"
    if not closed or naked_edges:
        return "FINISHING_AUDIT_BLOCKED_TOPOLOGY"
    if stone_collision:
        return "FINISHING_AUDIT_BLOCKED_STONE_COLLISION"
    return "FINISHING_AUDIT_REVIEW_REQUIRED"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Production Finishing Audit
# REPORT ONLY: never moves, trims, deletes, Booleans, or exports geometry.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
MIN_MEMBER_MM = 0.80
MIN_PRONG_TRIM_MM = 0.80
MAX_PRONG_TRIM_MM = 2.50
MAX_SYMMETRY_SPREAD_MM = 0.25
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)


def name_of(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj = sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None


def naked_count(brep):
    try:
        curves = brep.DuplicateNakedEdgeCurves(True, True)
        return len(curves) if curves else 0
    except Exception:
        return -1


def bbox(object_id):
    box = rs.BoundingBox(object_id)
    if not box:
        return None
    xs = [p.X for p in box]
    ys = [p.Y for p in box]
    zs = [p.Z for p in box]
    return {
        "min_x": min(xs), "max_x": max(xs),
        "min_y": min(ys), "max_y": max(ys),
        "min_z": min(zs), "max_z": max(zs),
    }


def min_section(object_id):
    box = bbox(object_id)
    if not box:
        return 0.0
    dimensions = [
        box["max_x"] - box["min_x"],
        box["max_y"] - box["min_y"],
        box["max_z"] - box["min_z"],
    ]
    positive = [value for value in dimensions if value > MODEL_TOLERANCE]
    return min(positive) if positive else 0.0


def intersects(first, second):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(
            first, second, MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def main():
    candidates = []
    prongs = []
    supports = []
    stone_id = None
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        upper = name_of(object_id).upper()
        if upper == "PTR_PRODUCTION_CANDIDATE_REVIEW_ONLY":
            candidates.append(object_id)
        elif "11DEG_REPOSITION_COPY" in upper and upper.startswith("PTR_PRONG_"):
            prongs.append(object_id)
        elif upper.startswith("PTR_CURVED_SUPPORT_TRIAL_"):
            supports.append(object_id)
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper
            and not any(word in upper for word in ("TRIAL", "COPY", "REHEARSAL", "RESULT"))
        ):
            stone_id = object_id

    candidate_id = candidates[0] if len(candidates) == 1 else None
    candidate_brep = brep_for(candidate_id) if candidate_id else None
    stone_brep = brep_for(stone_id) if stone_id else None
    closed = bool(candidate_id and rs.IsObjectSolid(candidate_id))
    naked = naked_count(candidate_brep) if candidate_brep else -1
    stone_collision = intersects(candidate_brep, stone_brep) if candidate_brep and stone_brep else False
    stone_box = bbox(stone_id) if stone_id else None

    prong_rows = []
    trim_values = []
    for object_id in sorted(prongs, key=name_of):
        box = bbox(object_id)
        trim = box["max_z"] - stone_box["max_z"] if box and stone_box else None
        if trim is not None:
            trim_values.append(trim)
        prong_rows.append({
            "name": name_of(object_id),
            "reference_diameter_mm": round(min_section(object_id), 3),
            "trim_allowance_mm": round(trim, 3) if trim is not None else None,
            "trim_status": (
                "TRIM_ALLOWANCE_OK" if trim is not None and MIN_PRONG_TRIM_MM <= trim <= MAX_PRONG_TRIM_MM
                else "TRIM_REQUIRED"
            ),
        })

    trim_spread = max(trim_values) - min(trim_values) if trim_values else None
    support_rows = [{
        "name": name_of(object_id),
        "reference_diameter_mm": round(min_section(object_id), 3),
        "shape": "CURVED",
        "junction_inspection": "PROFESSIONAL_VISUAL_AND_SECTION_CHECK_REQUIRED",
    } for object_id in sorted(supports, key=name_of)]

    if len(candidates) != 1:
        status = "FINISHING_AUDIT_BLOCKED_CANDIDATE"
    elif len(prongs) != 4 or len(supports) != 2:
        status = "FINISHING_AUDIT_BLOCKED_MEMBER_COUNT"
    elif not closed or naked:
        status = "FINISHING_AUDIT_BLOCKED_TOPOLOGY"
    elif stone_collision:
        status = "FINISHING_AUDIT_BLOCKED_STONE_COLLISION"
    else:
        status = "FINISHING_AUDIT_REVIEW_REQUIRED"

    blockers = []
    warnings = []
    if stone_id is None:
        blockers.append("Stone Placeholder is required.")
    if len(candidates) != 1:
        blockers.append("Exactly one review Production Candidate is required.")
    if len(prongs) != 4:
        blockers.append("Exactly four 11-degree trial prongs are required.")
    if len(supports) != 2:
        blockers.append("Exactly two curved trial supports are required.")
    for row in prong_rows:
        if row["reference_diameter_mm"] < MIN_MEMBER_MM:
            blockers.append(row["name"] + " is below minimum reference diameter.")
        if row["trim_status"] != "TRIM_ALLOWANCE_OK":
            warnings.append(row["name"] + " requires professional trim-height review.")
    for row in support_rows:
        if row["reference_diameter_mm"] < MIN_MEMBER_MM:
            blockers.append(row["name"] + " is below minimum reference diameter.")
    if trim_spread is not None and trim_spread > MAX_SYMMETRY_SPREAD_MM:
        warnings.append("Prong trim-height symmetry spread exceeds limit.")
    warnings.append("Inspect every curved-support junction with Section/ClippingPlane before production.")
    warnings.append("Confirm the stone insertion path and final prong folding allowance at the bench.")

    report = {
        "generator": "ptr-production-finishing-audit-v1",
        "status": status,
        "candidate_count": len(candidates),
        "candidate_closed": closed,
        "candidate_naked_edges": naked,
        "stone_collision": stone_collision,
        "prongs": prong_rows,
        "prong_trim_spread_mm": round(trim_spread, 3) if trim_spread is not None else None,
        "supports": support_rows,
        "blockers": blockers,
        "warnings": warnings,
        "geometry_modified": False,
        "temporary_geometry_added": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "professional_inspection_required": True,
    }
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("PRODUCTION FINISHING AUDIT | status=" + status)
    print("CANDIDATE | count={0} | closed={1} | naked_edges={2} | stone_collision={3}".format(
        len(candidates), closed, naked, stone_collision
    ))
    for row in prong_rows:
        print("PRONG FINISH | {0} | diameter_mm={1:.3f} | trim_allowance_mm={2} | {3}".format(
            row["name"], row["reference_diameter_mm"], row["trim_allowance_mm"], row["trim_status"]
        ))
    print("PRONG TRIM SYMMETRY | spread_mm=" + str(round(trim_spread, 3) if trim_spread is not None else None))
    for row in support_rows:
        print("SUPPORT FINISH | {0} | diameter_mm={1:.3f} | CURVED | JUNCTION_REVIEW_REQUIRED".format(
            row["name"], row["reference_diameter_mm"]
        ))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    for warning in warnings:
        print("WARNING | " + warning)
    print("GEOMETRY MODIFIED | NO")
    print("TEMPORARY GEOMETRY ADDED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED")
    print("FINISHING AUDIT REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_production_finishing_audit_script(report_path):
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/"))
    )


def prepare_production_finishing_audit(memory_root, now=None):
    stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_production_finishing_audit.py"
    report_path = memory_root / "Production_Finishing_Audits" / f"{stamp}_production_finishing_audit.json"
    return script_path, report_path, build_production_finishing_audit_script(report_path)


def save_production_finishing_audit(script_path, script):
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
