"""Generate a report-only Rhino 8 connection and shoulder plan."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


GENERATOR_VERSION = "ptr-connection-shoulder-planner-v1"


def build_connection_shoulder_plan_script(output_report_json: Path) -> str:
    """Return a Rhino script that proposes two shoulder bridges without editing."""
    output_text = str(output_report_json).replace("\\", "/")
    template = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Connection Shoulder Planner
# Generator: ptr-connection-shoulder-planner-v1
# REPORT ONLY: never creates, Boolean-unions, deletes, moves, or exports geometry.
import io
import json
import math
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_REPORT = r"__OUTPUT_REPORT__"
GENERATOR = "ptr-connection-shoulder-planner-v1"
SETTING_MARKERS = ("STONE_SEAT", "PRONG", "BASKET_SUPPORT", "PRODUCTION_METAL")
MIN_OVERLAP_MM = 0.30
DEFAULT_SHOULDER_WIDTH_MM = 1.60
DEFAULT_SHOULDER_THICKNESS_MM = 1.20


def point_data(x, y, z):
    return {"x": round(x, 4), "y": round(y, 4), "z": round(z, 4)}


def object_brep(obj_id):
    rhino_object = sc.doc.Objects.FindId(obj_id)
    if not rhino_object:
        return None
    return Rhino.Geometry.Brep.TryConvertBrep(rhino_object.Geometry)


def union_box(boxes):
    result = Rhino.Geometry.BoundingBox.Empty
    for box in boxes:
        result.Union(box)
    return result


def distance(left, right):
    dx = right["x"] - left["x"]
    dy = right["y"] - left["y"]
    dz = right["z"] - left["z"]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def main():
    band = None
    setting_parts = []
    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or "UNNAMED"
        upper = name.upper()
        brep = object_brep(obj_id)
        if not brep:
            continue
        item = {"name": name, "box": brep.GetBoundingBox(True)}
        if "RING_BAND" in upper and band is None:
            band = item
        elif any(marker in upper for marker in SETTING_MARKERS):
            setting_parts.append(item)

    blockers = []
    warnings = [
        "Bounding Box anchors are planning references, not verified surface contact points.",
        "A jewelry CAD professional must verify thickness, comfort, casting flow, and polishing access.",
    ]
    bridges = []
    band_to_setting_gap_mm = None

    if band is None:
        blockers.append("ไม่พบ RING_BAND ตามมาตรฐานการตั้งชื่อ PTR")
    if not setting_parts:
        blockers.append("ไม่พบชุดกระเปาะตามมาตรฐานการตั้งชื่อ PTR")

    if band is not None and setting_parts:
        band_box = band["box"]
        setting_box = union_box([item["box"] for item in setting_parts])
        center_x = (setting_box.Min.X + setting_box.Max.X) / 2.0
        center_y = (setting_box.Min.Y + setting_box.Max.Y) / 2.0
        setting_width_x = setting_box.Max.X - setting_box.Min.X
        anchor_offset_x = max(setting_width_x * 0.38, DEFAULT_SHOULDER_WIDTH_MM)
        band_top_z = band_box.Max.Z
        setting_bottom_z = setting_box.Min.Z
        band_to_setting_gap_mm = max(0.0, setting_bottom_z - band_top_z)

        band_anchor_z = band_top_z - MIN_OVERLAP_MM
        setting_anchor_z = setting_bottom_z + MIN_OVERLAP_MM
        for side, direction in (("LEFT", -1.0), ("RIGHT", 1.0)):
            x = center_x + direction * anchor_offset_x
            start = point_data(x, center_y, band_anchor_z)
            end = point_data(x, center_y, setting_anchor_z)
            bridges.append({
                "side": side,
                "status": "SHOULDER_BRIDGE_CANDIDATE",
                "band_anchor": start,
                "setting_anchor": end,
                "estimated_centerline_length_mm": round(distance(start, end), 4),
                "minimum_overlap_each_end_mm": MIN_OVERLAP_MM,
                "starting_width_mm": DEFAULT_SHOULDER_WIDTH_MM,
                "starting_thickness_mm": DEFAULT_SHOULDER_THICKNESS_MM,
                "requires_surface_projection": True,
                "requires_manual_review": True,
            })

        if band_to_setting_gap_mm <= float(sc.doc.ModelAbsoluteTolerance):
            warnings.append("Bounding Boxes already overlap; confirm whether existing parts truly intersect.")
        else:
            blockers.append(
                "ต้องสร้างและตรวจไหล่เชื่อมสองข้างก่อนรวมก้านแหวนกับชุดกระเปาะ"
            )

    payload = {
        "generator": GENERATOR,
        "status": "SHOULDER_PLAN_REVIEW_REQUIRED",
        "document_modified": False,
        "geometry_created": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "ring_band": band["name"] if band else None,
        "setting_parts": [item["name"] for item in setting_parts],
        "band_to_setting_bbox_gap_mm": (
            round(band_to_setting_gap_mm, 4)
            if band_to_setting_gap_mm is not None else None
        ),
        "proposed_bridges": bridges,
        "blockers": blockers,
        "warnings": warnings,
    }

    folder = os.path.dirname(OUTPUT_REPORT)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with io.open(OUTPUT_REPORT, "w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, ensure_ascii=False, indent=2)

    print("CONNECTION SHOULDER PLAN | status=SHOULDER_PLAN_REVIEW_REQUIRED")
    print("RING BAND | " + (band["name"] if band else "NOT FOUND"))
    print("SETTING PARTS | count=" + str(len(setting_parts)))
    if band_to_setting_gap_mm is not None:
        print("BAND TO SETTING BBOX GAP MM | " + str(round(band_to_setting_gap_mm, 4)))
    for bridge in bridges:
        print(
            bridge["side"] + " SHOULDER CANDIDATE | length_mm="
            + str(bridge["estimated_centerline_length_mm"])
            + " | width_mm=" + str(bridge["starting_width_mm"])
            + " | thickness_mm=" + str(bridge["starting_thickness_mm"])
        )
    print("GEOMETRY CREATED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("SHOULDER PLAN JSON | " + OUTPUT_REPORT)
    print("No geometry was modified.")


if __name__ == "__main__":
    main()
'''
    return template.replace("__OUTPUT_REPORT__", output_text)


def prepare_shoulder_plan_paths(memory_root: Path) -> tuple[Path, Path]:
    """Return unique script and shoulder-plan JSON paths."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    report_dir = memory_root / "Shoulder_Plans"
    script_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    return (
        script_dir / f"{stamp}_shoulder_plan.py",
        report_dir / f"{stamp}_shoulder_plan.json",
    )


def save_connection_shoulder_plan_script(path: Path, script: str) -> str:
    path.write_text(script, encoding="utf-8")
    return str(path)
