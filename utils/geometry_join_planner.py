"""Generate a report-only Rhino 8 geometry join plan."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


GENERATOR_VERSION = "ptr-geometry-join-planner-v1"


def build_geometry_join_plan_script(output_report_json: Path) -> str:
    """Return a Rhino script that proposes join groups without editing geometry."""
    output_text = str(output_report_json).replace("\\", "/")
    return f'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Geometry Join Planner
# Generator: {GENERATOR_VERSION}
# REPORT ONLY: never Boolean-unions, deletes, moves, renames, or exports geometry.
import io
import json
import math
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_REPORT = r"{output_text}"
GENERATOR = "{GENERATOR_VERSION}"
METAL_MARKERS = ("RING_BAND", "STONE_SEAT", "PRONG", "BASKET_SUPPORT", "PRODUCTION_METAL")
MIN_CONTACT_TOLERANCE_MM = 0.05


def is_metal(name):
    upper = (name or "").upper()
    return any(marker in upper for marker in METAL_MARKERS)


def axis_gap(a_min, a_max, b_min, b_max):
    if a_max < b_min:
        return b_min - a_max
    if b_max < a_min:
        return a_min - b_max
    return 0.0


def bounding_box_gap(box_a, box_b):
    dx = axis_gap(box_a.Min.X, box_a.Max.X, box_b.Min.X, box_b.Max.X)
    dy = axis_gap(box_a.Min.Y, box_a.Max.Y, box_b.Min.Y, box_b.Max.Y)
    dz = axis_gap(box_a.Min.Z, box_a.Max.Z, box_b.Min.Z, box_b.Max.Z)
    return math.sqrt(dx * dx + dy * dy + dz * dz), [dx, dy, dz]


def find_root(parent, node):
    while parent[node] != node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node


def union(parent, left, right):
    root_left = find_root(parent, left)
    root_right = find_root(parent, right)
    if root_left != root_right:
        parent[root_right] = root_left


def main():
    tolerance = max(float(sc.doc.ModelAbsoluteTolerance) * 2.0, MIN_CONTACT_TOLERANCE_MM)
    metals = []
    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or "UNNAMED"
        if not is_metal(name):
            continue
        rhino_object = sc.doc.Objects.FindId(obj_id)
        brep = (
            Rhino.Geometry.Brep.TryConvertBrep(rhino_object.Geometry)
            if rhino_object else None
        )
        if not brep:
            continue
        box = brep.GetBoundingBox(True)
        metals.append({{
            "name": name,
            "closed_solid": bool(brep.IsSolid),
            "box": box,
        }})

    parent = list(range(len(metals)))
    pairs = []
    for left_index in range(len(metals)):
        for right_index in range(left_index + 1, len(metals)):
            left = metals[left_index]
            right = metals[right_index]
            gap, axis_gaps = bounding_box_gap(left["box"], right["box"])
            candidate = gap <= tolerance
            if candidate:
                union(parent, left_index, right_index)
            pairs.append({{
                "left": left["name"],
                "right": right["name"],
                "status": "CONTACT_CANDIDATE" if candidate else "SEPARATE",
                "bounding_box_gap_mm": round(gap, 4),
                "axis_gaps_mm": [round(value, 4) for value in axis_gaps],
                "requires_manual_surface_check": True,
            }})

    groups_by_root = {{}}
    for index, metal in enumerate(metals):
        root = find_root(parent, index)
        groups_by_root.setdefault(root, []).append(metal["name"])
    groups = list(groups_by_root.values())

    blockers = []
    if not metals:
        blockers.append("ไม่พบชิ้นส่วนโลหะที่ตั้งชื่อตามมาตรฐาน PTR")
    if len(groups) > 1:
        blockers.append(
            "ชิ้นส่วนโลหะแบ่งเป็น " + str(len(groups))
            + " กลุ่มที่ยังไม่เชื่อมต่อกันตาม Bounding Box"
        )
    blockers.append("ต้องให้ช่างยืนยันผิวสัมผัสจริงก่อนทำ Boolean Union")

    payload = {{
        "generator": GENERATOR,
        "status": "JOIN_PLAN_REVIEW_REQUIRED",
        "document_modified": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "contact_tolerance_mm": tolerance,
        "metal_count": len(metals),
        "candidate_pair_count": len([pair for pair in pairs if pair["status"] == "CONTACT_CANDIDATE"]),
        "separate_pair_count": len([pair for pair in pairs if pair["status"] == "SEPARATE"]),
        "proposed_join_groups": groups,
        "pairs": pairs,
        "blockers": blockers,
    }}

    folder = os.path.dirname(OUTPUT_REPORT)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with io.open(OUTPUT_REPORT, "w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, ensure_ascii=False, indent=2)

    print("GEOMETRY JOIN PLAN | status=JOIN_PLAN_REVIEW_REQUIRED")
    print("METAL OBJECTS | count=" + str(len(metals)))
    print("CONTACT TOLERANCE MM | " + str(tolerance))
    print("PROPOSED GROUPS | count=" + str(len(groups)))
    for group_index, group in enumerate(groups):
        print("GROUP " + str(group_index + 1) + " | " + ", ".join(group))
    for pair in pairs:
        if pair["status"] == "CONTACT_CANDIDATE":
            print(
                "CONTACT CANDIDATE | " + pair["left"] + " <-> " + pair["right"]
                + " | bbox_gap_mm=" + str(pair["bounding_box_gap_mm"])
            )
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("JOIN PLAN JSON | " + OUTPUT_REPORT)
    print("No geometry was modified.")


if __name__ == "__main__":
    main()
'''


def prepare_join_plan_paths(memory_root: Path) -> tuple[Path, Path]:
    """Return unique script and join-plan JSON paths."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    report_dir = memory_root / "Join_Plans"
    script_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    return (
        script_dir / f"{stamp}_join_plan.py",
        report_dir / f"{stamp}_join_plan.json",
    )


def save_geometry_join_plan_script(path: Path, script: str) -> str:
    path.write_text(script, encoding="utf-8")
    return str(path)
