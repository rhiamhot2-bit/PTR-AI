"""Generate a report-only Production Finishing Plan."""

from datetime import datetime
import json
from pathlib import Path


MIN_TRIM_ALLOWANCE_MM = 0.80
MAX_TRIM_ALLOWANCE_MM = 2.50


def prong_finishing_action(allowance_mm, minimum=MIN_TRIM_ALLOWANCE_MM, maximum=MAX_TRIM_ALLOWANCE_MM):
    if allowance_mm < minimum:
        return "LENGTHEN_OR_REBUILD", round(minimum - allowance_mm, 3)
    if allowance_mm > maximum:
        return "TRIM", round(allowance_mm - maximum, 3)
    return "KEEP_FOR_BENCH_SETTING", 0.0


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Production Finishing Plan
# PLAN ONLY: never moves, trims, deletes, Booleans, or exports geometry.
import io
import json
import os

import rhinoscriptsyntax as rs

REPORT_PATH = __REPORT_PATH__
MIN_TRIM_ALLOWANCE_MM = 0.80
MAX_TRIM_ALLOWANCE_MM = 2.50
MAX_SYMMETRY_SPREAD_MM = 0.25


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def bounds(object_id):
    box = rs.BoundingBox(object_id)
    if not box:
        return None
    xs = [point.X for point in box]
    ys = [point.Y for point in box]
    zs = [point.Z for point in box]
    return {
        "min_x": min(xs), "max_x": max(xs),
        "min_y": min(ys), "max_y": max(ys),
        "min_z": min(zs), "max_z": max(zs),
    }


def minimum_section(object_id):
    box = bounds(object_id)
    if not box:
        return 0.0
    values = [
        box["max_x"] - box["min_x"],
        box["max_y"] - box["min_y"],
        box["max_z"] - box["min_z"],
    ]
    positive = [value for value in values if value > 0.000001]
    return min(positive) if positive else 0.0


def action_for(allowance):
    if allowance < MIN_TRIM_ALLOWANCE_MM:
        return "LENGTHEN_OR_REBUILD", MIN_TRIM_ALLOWANCE_MM - allowance
    if allowance > MAX_TRIM_ALLOWANCE_MM:
        return "TRIM", allowance - MAX_TRIM_ALLOWANCE_MM
    return "KEEP_FOR_BENCH_SETTING", 0.0


def main():
    candidates = []
    prongs = []
    supports = []
    stone_id = None
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        upper = object_name(object_id).upper()
        if upper == "PTR_PRODUCTION_CANDIDATE_REVIEW_ONLY":
            candidates.append(object_id)
        elif upper.startswith("PTR_PRONG_") and "11DEG_REPOSITION_COPY" in upper:
            prongs.append(object_id)
        elif upper.startswith("PTR_CURVED_SUPPORT_TRIAL_"):
            supports.append(object_id)
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper
            and not any(word in upper for word in ("TRIAL", "COPY", "REHEARSAL", "RESULT"))
        ):
            stone_id = object_id

    stone_box = bounds(stone_id) if stone_id else None
    plans = []
    allowances = []
    for object_id in sorted(prongs, key=object_name):
        box = bounds(object_id)
        allowance = box["max_z"] - stone_box["max_z"] if box and stone_box else None
        if allowance is None:
            action, adjustment = "MANUAL_MEASUREMENT_REQUIRED", None
        else:
            action, adjustment = action_for(allowance)
            allowances.append(allowance)
        plans.append({
            "name": object_name(object_id),
            "diameter_mm": round(minimum_section(object_id), 3),
            "allowance_mm": round(allowance, 3) if allowance is not None else None,
            "action": action,
            "minimum_addition_or_maximum_removal_mm": (
                round(adjustment, 3) if adjustment is not None else None
            ),
            "preserve_outward_tilt_deg": 11.0,
            "minimum_seat_engagement_ratio": 0.25,
        })

    spread = max(allowances) - min(allowances) if allowances else None
    support_plans = [{
        "name": object_name(object_id),
        "diameter_mm": round(minimum_section(object_id), 3),
        "action": "KEEP_GEOMETRY_INSPECT_JUNCTIONS",
        "top_contact_target_percent": 100,
        "bottom_contact_target_percent": 100,
        "inspection": "SECTION_OR_CLIPPING_PLANE_TOP_AND_BOTTOM",
    } for object_id in sorted(supports, key=object_name)]

    blockers = []
    if len(candidates) != 1:
        blockers.append("Exactly one review Production Candidate is required.")
    if stone_id is None:
        blockers.append("Stone Placeholder is required.")
    if len(prongs) != 4:
        blockers.append("Exactly four 11-degree trial prongs are required.")
    if len(supports) != 2:
        blockers.append("Exactly two curved trial supports are required.")
    if spread is not None and spread > MAX_SYMMETRY_SPREAD_MM:
        blockers.append("Prong allowance symmetry spread exceeds 0.25 mm.")

    if blockers:
        status = "PRODUCTION_FINISHING_PLAN_BLOCKED"
    elif any(row["action"] == "LENGTHEN_OR_REBUILD" for row in plans):
        status = "PRODUCTION_FINISHING_PLAN_REBUILD_REVIEW_REQUIRED"
    elif any(row["action"] == "TRIM" for row in plans):
        status = "PRODUCTION_FINISHING_PLAN_TRIM_REVIEW_REQUIRED"
    else:
        status = "PRODUCTION_FINISHING_PLAN_BENCH_REVIEW_REQUIRED"

    report = {
        "generator": "ptr-production-finishing-plan-v1",
        "status": status,
        "candidate_count": len(candidates),
        "prong_plans": plans,
        "prong_allowance_spread_mm": round(spread, 3) if spread is not None else None,
        "support_plans": support_plans,
        "stone_insertion_path_action": "CONFIRM_FROM_TOP_BEFORE_BENCH_SETTING",
        "blockers": blockers,
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

    print("PRODUCTION FINISHING PLAN | status=" + status)
    for row in plans:
        print("PRONG PLAN | {0} | allowance_mm={1} | action={2} | adjustment_mm={3} | preserve_outward_tilt_deg=11.0 | engagement_ratio>=0.25".format(
            row["name"], row["allowance_mm"], row["action"],
            row["minimum_addition_or_maximum_removal_mm"]
        ))
    print("PRONG SYMMETRY | spread_mm=" + str(round(spread, 3) if spread is not None else None))
    for row in support_plans:
        print("SUPPORT PLAN | {0} | action={1} | top_contact=100% | bottom_contact=100% | {2}".format(
            row["name"], row["action"], row["inspection"]
        ))
    print("STONE INSERTION PATH | CONFIRM FROM TOP BEFORE BENCH SETTING")
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("TEMPORARY GEOMETRY ADDED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED")
    print("FINISHING PLAN REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_production_finishing_plan_script(report_path):
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/"))
    )


def prepare_production_finishing_plan(memory_root, now=None):
    stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_production_finishing_plan.py"
    report_path = memory_root / "Production_Finishing_Plans" / f"{stamp}_production_finishing_plan.json"
    return script_path, report_path, build_production_finishing_plan_script(report_path)


def save_production_finishing_plan(script_path, script):
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
