"""Generate a report-only Prong 11° and Curved Support Reposition Planner."""

from datetime import datetime
import json
from pathlib import Path

PRONG_OUTWARD_TILT_DEG = 11.0
MIN_PRONG_ENGAGEMENT_RATIO = 0.25


def required_prong_engagement_mm(diameter_mm: float) -> float:
    return round(diameter_mm * MIN_PRONG_ENGAGEMENT_RATIO, 3)


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Prong and Curved Support Reposition Planner
# REPORT ONLY: does not transform or create geometry.
import io
import json
import os

import rhinoscriptsyntax as rs

REPORT_PATH = __REPORT_PATH__
PRONG_OUTWARD_TILT_DEG = 11.0
MIN_PRONG_ENGAGEMENT_RATIO = 0.25


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def original_role(name):
    value = name.upper()
    if any(marker in value for marker in ("REHEARSAL", "TRIAL", "COPY", "RESULT", "STONE_PLACEHOLDER", "GIRDLE_GUIDE")):
        return None
    if "STONE_SEAT" in value:
        return "SEAT"
    if "PRONG" in value:
        return "PRONG"
    if "BASKET_SUPPORT" in value:
        return "SUPPORT"
    if "RING_BAND" in value:
        return "BAND"
    return None


def bbox_dimensions(object_id):
    corners = rs.BoundingBox(object_id)
    if not corners:
        return None
    values = [(point.X, point.Y, point.Z) for point in corners]
    return [
        max(point[axis] for point in values) - min(point[axis] for point in values)
        for axis in range(3)
    ]


def estimated_uniform_prong_diameter(object_id):
    dimensions = bbox_dimensions(object_id)
    if not dimensions:
        return None
    dimensions.sort()
    return (dimensions[0] + dimensions[1]) / 2.0


def main():
    seats = []
    prongs = []
    supports = []
    bands = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        role = original_role(name)
        if role is None or not rs.IsObjectSolid(object_id):
            continue
        item = {"id": str(object_id), "name": name}
        if role == "SEAT":
            seats.append(item)
        elif role == "PRONG":
            diameter = estimated_uniform_prong_diameter(object_id)
            item.update({
                "uniform_diameter_required": True,
                "estimated_diameter_mm": round(diameter, 6) if diameter is not None else None,
                "target_outward_tilt_deg": PRONG_OUTWARD_TILT_DEG,
                "minimum_engagement_ratio": MIN_PRONG_ENGAGEMENT_RATIO,
                "minimum_engagement_mm": round(diameter * MIN_PRONG_ENGAGEMENT_RATIO, 6) if diameter is not None else None,
                "placement_intent": "Tilt the complete uniform-diameter prong outward so the stone drops in without pre-opening; reposition the base into the seat.",
            })
            prongs.append(item)
        elif role == "SUPPORT":
            item.update({
                "style": "CURVED_SYMMETRIC_SUPPORT",
                "top_contact_requirement": "100_PERCENT_CONTACT_WITH_STONE_SEAT",
                "bottom_contact_requirement": "100_PERCENT_CONTACT_WITH_RING_BAND",
                "top_direction": "CURVE_OUTWARD_TO_SEAT",
                "bottom_direction": "CURVE_TO_RING_SHANK",
                "placement_intent": "Rebuild or bend the support curve; do not translate the entire straight post.",
            })
            supports.append(item)
        elif role == "BAND":
            bands.append(item)

    blockers = []
    if len(seats) != 1:
        blockers.append("Exactly one original Stone Seat is required.")
    if len(prongs) != 4:
        blockers.append("Exactly four original Prongs are required.")
    if len(supports) != 2:
        blockers.append("Exactly two original Basket Supports are required.")
    if len(bands) != 1:
        blockers.append("Exactly one original Ring Band is required.")

    report = {
        "generator": "ptr-prong-support-reposition-planner-v1",
        "status": "REPOSITION_PLAN_REVIEW_REQUIRED" if not blockers else "REPOSITION_PLAN_BLOCKED",
        "stone_seat": seats,
        "ring_band": bands,
        "prong_plan": prongs,
        "support_plan": supports,
        "design_rules": {
            "prong_uniform_diameter": True,
            "prong_outward_tilt_deg": PRONG_OUTWARD_TILT_DEG,
            "minimum_prong_engagement_ratio": MIN_PRONG_ENGAGEMENT_RATIO,
            "stone_loading_goal": "STONE_DROPS_IN_WITHOUT_PRONG_PRE_OPENING",
            "support_pair_symmetry_required": True,
            "support_top_full_contact_required": True,
            "support_bottom_full_contact_required": True,
            "bridge_connector_strategy": "FALLBACK_FOR_SPECIAL_REPAIR_CASES_ONLY",
        },
        "blockers": blockers,
        "geometry_modified": False,
        "production_export_allowed": False,
        "professional_review_required": True,
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("PRONG & SUPPORT REPOSITION PLANNER | status=" + report["status"])
    for item in prongs:
        print("PRONG PLAN | {0} | diameter_mm={1} | tilt_deg=11.0 | min_engagement_mm={2}".format(
            item["name"], item["estimated_diameter_mm"], item["minimum_engagement_mm"]))
    for item in supports:
        print("SUPPORT PLAN | {0} | CURVED | top_contact=100% | bottom_contact=100%".format(item["name"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("BRIDGE CONNECTORS | FALLBACK ONLY")
    print("GEOMETRY MODIFIED | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("REPOSITION PLAN | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_prong_support_reposition_planner_script(report_path: Path) -> str:
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/")))


def prepare_prong_support_reposition_planner(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_prong_support_reposition_plan.py"
    report_path = memory_root / "Prong_Support_Reposition_Plans" / f"{timestamp}_prong_support_reposition_plan.json"
    return script_path, report_path, build_prong_support_reposition_planner_script(report_path)


def save_prong_support_reposition_planner(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
