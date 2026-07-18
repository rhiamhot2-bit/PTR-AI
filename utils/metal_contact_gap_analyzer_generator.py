"""Generate a non-destructive Rhino 8 metal contact-gap analyzer."""

from datetime import datetime
import json
from pathlib import Path

GENERATOR_ID = "ptr-metal-contact-gap-analyzer-v1"
INCLUDE_MARKERS = (
    "RING_BAND",
    "STONE_SEAT",
    "PRONG",
    "BASKET_SUPPORT",
    "SHOULDER",
    "PRODUCTION_METAL",
)
EXCLUDE_MARKERS = (
    "STONE_PLACEHOLDER",
    "GIRDLE_GUIDE",
    "GUIDE",
    "NOTES",
    "REHEARSAL_COPY",
    "METAL_UNION_REHEARSAL_RESULT",
)


def is_gap_analyzer_metal_name(name: str) -> bool:
    """Return True only for named original metal candidates."""
    upper_name = (name or "").upper()
    return (
        any(marker in upper_name for marker in INCLUDE_MARKERS)
        and not any(marker in upper_name for marker in EXCLUDE_MARKERS)
    )


def classify_bbox_gap(gap_mm: float, intersects: bool) -> str:
    """Classify a read-only broad-phase pair result."""
    if intersects:
        return "INTERSECTING"
    if gap_mm <= 0.05:
        return "CONTACT_CANDIDATE"
    if gap_mm <= 0.30:
        return "SMALL_GAP"
    return "OPEN_GAP"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Metal Contact Gap Analyzer
# Generator: ptr-metal-contact-gap-analyzer-v1
# REPORT ONLY: geometry is never copied, Booleaned, deleted, moved, renamed, or exported.
import io
import itertools
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)
CONTACT_TOLERANCE_MM = max(0.05, MODEL_TOLERANCE)
SMALL_GAP_LIMIT_MM = 0.30
INCLUDE_MARKERS = (
    "RING_BAND",
    "STONE_SEAT",
    "PRONG",
    "BASKET_SUPPORT",
    "SHOULDER",
    "PRODUCTION_METAL",
)
EXCLUDE_MARKERS = (
    "STONE_PLACEHOLDER",
    "GIRDLE_GUIDE",
    "GUIDE",
    "NOTES",
    "REHEARSAL_COPY",
    "METAL_UNION_REHEARSAL_RESULT",
)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def is_gap_analyzer_metal(object_id):
    name = object_name(object_id).upper()
    return (
        any(marker in name for marker in INCLUDE_MARKERS)
        and not any(marker in name for marker in EXCLUDE_MARKERS)
    )


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


def axis_gap(a_min, a_max, b_min, b_max):
    return max(0.0, b_min - a_max, a_min - b_max)


def bbox_gap(a, b):
    dx = axis_gap(a.Min.X, a.Max.X, b.Min.X, b.Max.X)
    dy = axis_gap(a.Min.Y, a.Max.Y, b.Min.Y, b.Max.Y)
    dz = axis_gap(a.Min.Z, a.Max.Z, b.Min.Z, b.Max.Z)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def bbox_overlaps(a, b, tolerance):
    return (
        a.Min.X <= b.Max.X + tolerance
        and a.Max.X + tolerance >= b.Min.X
        and a.Min.Y <= b.Max.Y + tolerance
        and a.Max.Y + tolerance >= b.Min.Y
        and a.Min.Z <= b.Max.Z + tolerance
        and a.Max.Z + tolerance >= b.Min.Z
    )


def breps_intersect(a, b):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(
            a, b, MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def classify(gap_mm, intersects):
    if intersects:
        return "INTERSECTING"
    if gap_mm <= CONTACT_TOLERANCE_MM:
        return "CONTACT_CANDIDATE"
    if gap_mm <= SMALL_GAP_LIMIT_MM:
        return "SMALL_GAP"
    return "OPEN_GAP"


def recommendation(status, gap_mm):
    if status == "INTERSECTING":
        return "Inspect overlap depth; pair may be eligible for union rehearsal."
    if status == "CONTACT_CANDIDATE":
        return "Verify real surface contact with Rhino inspection tools."
    if status == "SMALL_GAP":
        return "Extend or reposition metal by at least {0:.3f} mm plus safe overlap.".format(gap_mm)
    return "Connection geometry or a larger extension is required."


def write_report(report):
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, ensure_ascii=False, indent=2)


def main():
    objects = []
    invalid_objects = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False):
        if not is_gap_analyzer_metal(object_id):
            continue
        brep = brep_for(object_id)
        item = {
            "id": str(object_id),
            "name": object_name(object_id),
            "closed_solid": bool(rs.IsObjectSolid(object_id)),
        }
        if brep is None or not item["closed_solid"]:
            invalid_objects.append(item)
            continue
        objects.append((object_id, item["name"], brep, brep.GetBoundingBox(True)))

    pairs = []
    counts = {
        "INTERSECTING": 0,
        "CONTACT_CANDIDATE": 0,
        "SMALL_GAP": 0,
        "OPEN_GAP": 0,
    }
    for left, right in itertools.combinations(objects, 2):
        left_id, left_name, left_brep, left_box = left
        right_id, right_name, right_brep, right_box = right
        gap_mm = bbox_gap(left_box, right_box)
        broad_phase_overlap = bbox_overlaps(left_box, right_box, MODEL_TOLERANCE)
        intersects = broad_phase_overlap and breps_intersect(left_brep, right_brep)
        status = classify(gap_mm, intersects)
        counts[status] += 1
        pairs.append(
            {
                "left_id": str(left_id),
                "left_name": left_name,
                "right_id": str(right_id),
                "right_name": right_name,
                "status": status,
                "bbox_gap_mm": round(gap_mm, 6),
                "brep_intersection_detected": bool(intersects),
                "recommendation": recommendation(status, gap_mm),
            }
        )

    blockers = []
    if len(objects) < 2:
        blockers.append("At least two clean closed metal solids are required.")
    for item in invalid_objects:
        blockers.append("Invalid metal object: " + item["name"])

    report = {
        "generator": "ptr-metal-contact-gap-analyzer-v1",
        "status": "METAL_CONTACT_GAP_BLOCKED" if blockers else "METAL_CONTACT_GAP_REVIEW_REQUIRED",
        "measurement_method": "BRep intersection plus Bounding Box gap broad-phase estimate",
        "model_tolerance_mm": MODEL_TOLERANCE,
        "contact_tolerance_mm": CONTACT_TOLERANCE_MM,
        "small_gap_limit_mm": SMALL_GAP_LIMIT_MM,
        "metal_object_count": len(objects),
        "invalid_objects": invalid_objects,
        "pair_count": len(pairs),
        "status_counts": counts,
        "pairs": pairs,
        "geometry_modified": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "blockers": blockers,
    }

    print("METAL CONTACT GAP ANALYZER | status={0}".format(report["status"]))
    print("METAL OBJECTS | count={0}".format(len(objects)))
    print("PAIR CHECKS | count={0}".format(len(pairs)))
    for pair in pairs:
        print(
            "PAIR | {0} <-> {1} | {2} | bbox_gap_mm={3:.3f}".format(
                pair["left_name"],
                pair["right_name"],
                pair["status"],
                pair["bbox_gap_mm"],
            )
        )
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("CONTACT GAP AUDIT JSON | " + REPORT_PATH)
    print("Bounding Box gap is a screening estimate; professional Rhino inspection is required.")

    write_report(report)


if __name__ == "__main__":
    main()
'''


def build_metal_contact_gap_analyzer_script(report_path: Path) -> str:
    """Build the Rhino report-only analyzer script."""
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_metal_contact_gap_analyzer(
    memory_root: Path,
    now: datetime | None = None,
) -> tuple[Path, Path, str]:
    """Return script path, report path, and generated source."""
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_metal_contact_gaps.py"
    report_path = (
        memory_root
        / "Metal_Contact_Gaps"
        / f"{timestamp}_metal_contact_gaps.json"
    )
    return script_path, report_path, build_metal_contact_gap_analyzer_script(report_path)


def save_metal_contact_gap_analyzer(script_path: Path, script: str) -> None:
    """Persist the generated Rhino script."""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
