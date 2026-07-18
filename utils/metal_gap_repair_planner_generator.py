"""Generate a report-only Rhino 8 Metal Gap Repair Planner."""

from datetime import datetime
import json
from pathlib import Path

GENERATOR_ID = "ptr-metal-gap-repair-planner-v1"
SAFE_OVERLAP_MM = 0.15
MAX_SIMPLE_EXTENSION_MM = 1.50

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


def is_repair_plan_metal_name(name: str) -> bool:
    upper_name = (name or "").upper()
    return (
        any(marker in upper_name for marker in INCLUDE_MARKERS)
        and not any(marker in upper_name for marker in EXCLUDE_MARKERS)
    )


def classify_repair(gap_mm: float, intersects: bool) -> str:
    if intersects:
        return "NO_REPAIR_INTERSECTING"
    if gap_mm <= 0.05:
        return "VERIFY_CONTACT"
    if gap_mm <= MAX_SIMPLE_EXTENSION_MM:
        return "EXTENSION_CANDIDATE"
    return "NEW_CONNECTION_GEOMETRY_REQUIRED"


def extension_mm(gap_mm: float) -> float:
    return round(max(0.0, gap_mm) + SAFE_OVERLAP_MM, 3)


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Metal Gap Repair Planner
# REPORT ONLY: never changes model geometry.
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
SAFE_OVERLAP_MM = 0.15
MAX_SIMPLE_EXTENSION_MM = 1.50
INCLUDE_MARKERS = ("RING_BAND", "STONE_SEAT", "PRONG", "BASKET_SUPPORT", "SHOULDER", "PRODUCTION_METAL")
EXCLUDE_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "GUIDE", "NOTES", "REHEARSAL_COPY", "METAL_UNION_REHEARSAL_RESULT")


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def is_metal(object_id):
    name = object_name(object_id).upper()
    return any(marker in name for marker in INCLUDE_MARKERS) and not any(marker in name for marker in EXCLUDE_MARKERS)


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


def role(name):
    value = name.upper()
    for marker in ("RING_BAND", "STONE_SEAT", "PRONG", "BASKET_SUPPORT", "SHOULDER"):
        if marker in value:
            return marker
    return "PRODUCTION_METAL"


def intended_pair(left_name, right_name):
    pair = set((role(left_name), role(right_name)))
    return pair in (
        set(("STONE_SEAT", "PRONG")),
        set(("STONE_SEAT", "BASKET_SUPPORT")),
        set(("BASKET_SUPPORT", "RING_BAND")),
        set(("SHOULDER", "RING_BAND")),
        set(("SHOULDER", "BASKET_SUPPORT")),
    )


def axis_plan(a, b):
    axes = (
        ("X", a.Min.X, a.Max.X, b.Min.X, b.Max.X),
        ("Y", a.Min.Y, a.Max.Y, b.Min.Y, b.Max.Y),
        ("Z", a.Min.Z, a.Max.Z, b.Min.Z, b.Max.Z),
    )
    separated = []
    for axis, a_min, a_max, b_min, b_max in axes:
        if a_max < b_min:
            separated.append((b_min - a_max, axis, "POSITIVE_" + axis))
        elif b_max < a_min:
            separated.append((a_min - b_max, axis, "NEGATIVE_" + axis))
    if not separated:
        return {"axis": None, "direction": None, "gap_mm": 0.0}
    gap, axis, direction = min(separated)
    return {"axis": axis, "direction": direction, "gap_mm": gap}


def bbox_distance(a, b):
    gaps = []
    for a_min, a_max, b_min, b_max in (
        (a.Min.X, a.Max.X, b.Min.X, b.Max.X),
        (a.Min.Y, a.Max.Y, b.Min.Y, b.Max.Y),
        (a.Min.Z, a.Max.Z, b.Min.Z, b.Max.Z),
    ):
        gaps.append(max(0.0, b_min - a_max, a_min - b_max))
    return math.sqrt(sum(value * value for value in gaps))


def breps_intersect(a, b):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(a, b, MODEL_TOLERANCE)
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def repair_status(gap_mm, intersects):
    if intersects:
        return "NO_REPAIR_INTERSECTING"
    if gap_mm <= CONTACT_TOLERANCE_MM:
        return "VERIFY_CONTACT"
    if gap_mm <= MAX_SIMPLE_EXTENSION_MM:
        return "EXTENSION_CANDIDATE"
    return "NEW_CONNECTION_GEOMETRY_REQUIRED"


def main():
    objects = []
    invalid = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        if not is_metal(object_id):
            continue
        brep = brep_for(object_id)
        if brep is None or not rs.IsObjectSolid(object_id):
            invalid.append(object_name(object_id))
            continue
        objects.append((object_id, object_name(object_id), brep, brep.GetBoundingBox(True)))

    plans = []
    for left, right in itertools.combinations(objects, 2):
        left_id, left_name, left_brep, left_box = left
        right_id, right_name, right_brep, right_box = right
        if not intended_pair(left_name, right_name):
            continue
        gap_mm = bbox_distance(left_box, right_box)
        intersects = breps_intersect(left_brep, right_brep) if gap_mm <= CONTACT_TOLERANCE_MM else False
        status = repair_status(gap_mm, intersects)
        direction = axis_plan(left_box, right_box)
        proposed_extension = None
        if status == "EXTENSION_CANDIDATE":
            proposed_extension = round(gap_mm + SAFE_OVERLAP_MM, 3)
        plans.append({
            "source_id": str(left_id),
            "source_name": left_name,
            "target_id": str(right_id),
            "target_name": right_name,
            "status": status,
            "bbox_gap_mm": round(gap_mm, 6),
            "axis": direction["axis"],
            "direction_from_source_toward_target": direction["direction"],
            "safe_overlap_mm": SAFE_OVERLAP_MM,
            "proposed_extension_mm": proposed_extension,
            "instruction": (
                "Extend connection metal along the reported axis; do not move the entire source object."
                if status == "EXTENSION_CANDIDATE"
                else "Inspect real surfaces before deciding the repair."
                if status == "VERIFY_CONTACT"
                else "Design a new bridge/support; simple extension is not recommended."
                if status == "NEW_CONNECTION_GEOMETRY_REQUIRED"
                else "No repair proposed; inspect overlap depth."
            ),
        })

    blockers = ["Invalid metal object: " + name for name in invalid]
    report = {
        "generator": "ptr-metal-gap-repair-planner-v1",
        "status": "METAL_GAP_REPAIR_PLAN_REVIEW_REQUIRED",
        "measurement_method": "BRep intersection plus axis-aligned bounding-box screening",
        "safe_overlap_mm": SAFE_OVERLAP_MM,
        "maximum_simple_extension_mm": MAX_SIMPLE_EXTENSION_MM,
        "plans": plans,
        "blockers": blockers,
        "geometry_modified": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "professional_review_required": True,
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("METAL GAP REPAIR PLANNER | status=" + report["status"])
    for plan in plans:
        print("REPAIR PLAN | {0} -> {1} | {2} | gap_mm={3:.3f} | axis={4} | direction={5} | extension_mm={6}".format(
            plan["source_name"], plan["target_name"], plan["status"], plan["bbox_gap_mm"],
            plan["axis"], plan["direction_from_source_toward_target"], plan["proposed_extension_mm"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("REPAIR PLAN JSON | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_metal_gap_repair_planner_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_metal_gap_repair_planner(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_metal_gap_repair_plan.py"
    report_path = memory_root / "Metal_Gap_Repair_Plans" / f"{timestamp}_metal_gap_repair_plan.json"
    return script_path, report_path, build_metal_gap_repair_planner_script(report_path)


def save_metal_gap_repair_planner(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
