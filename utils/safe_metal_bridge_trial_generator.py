"""Generate a Rhino 8 preview-only Safe Metal Bridge Trial."""

from datetime import datetime
import json
from pathlib import Path

GENERATOR_ID = "ptr-safe-metal-bridge-trial-v1"
TRIAL_LAYER = "PTR_METAL_BRIDGE_TRIAL"
SAFE_OVERLAP_MM = 0.15
BRIDGE_RADIUS_MM = 0.45
MAX_TRIAL_GAP_MM = 1.50


def trial_span_mm(gap_mm: float) -> float:
    return round(max(0.0, gap_mm) + (2.0 * SAFE_OVERLAP_MM), 3)


def is_trial_gap(gap_mm: float) -> bool:
    return 0.05 < gap_mm <= MAX_TRIAL_GAP_MM


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Safe Metal Bridge Trial
# PREVIEW ONLY: adds bridge trial solids on a dedicated layer.
import io
import itertools
import json
import os

import rhinoscriptsyntax as rs

REPORT_PATH = __REPORT_PATH__
TRIAL_LAYER = "PTR_METAL_BRIDGE_TRIAL"
SAFE_OVERLAP_MM = 0.15
BRIDGE_RADIUS_MM = 0.45
MAX_TRIAL_GAP_MM = 1.50


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def role(name):
    value = name.upper()
    if "BASKET_SUPPORT" in value:
        return "BASKET_SUPPORT"
    if "RING_BAND" in value:
        return "RING_BAND"
    return None


def bbox_min_max(object_id):
    corners = rs.BoundingBox(object_id)
    if not corners:
        return None
    values = [(point.X, point.Y, point.Z) for point in corners]
    return (
        [min(point[i] for point in values) for i in range(3)],
        [max(point[i] for point in values) for i in range(3)],
    )


def separated_axis(first, second):
    candidates = []
    for axis in range(3):
        if first[1][axis] < second[0][axis]:
            candidates.append((second[0][axis] - first[1][axis], axis, 1))
        elif second[1][axis] < first[0][axis]:
            candidates.append((first[0][axis] - second[1][axis], axis, -1))
    if not candidates:
        return None
    return min(candidates)


def overlap_midpoint(first, second, axis):
    low = max(first[0][axis], second[0][axis])
    high = min(first[1][axis], second[1][axis])
    if low <= high:
        return (low + high) / 2.0
    first_center = (first[0][axis] + first[1][axis]) / 2.0
    second_center = (second[0][axis] + second[1][axis]) / 2.0
    return (first_center + second_center) / 2.0


def bridge_points(first, second, axis, direction):
    start = [0.0, 0.0, 0.0]
    end = [0.0, 0.0, 0.0]
    for other_axis in range(3):
        if other_axis != axis:
            coordinate = overlap_midpoint(first, second, other_axis)
            start[other_axis] = coordinate
            end[other_axis] = coordinate
    if direction > 0:
        start[axis] = first[1][axis] - SAFE_OVERLAP_MM
        end[axis] = second[0][axis] + SAFE_OVERLAP_MM
    else:
        start[axis] = first[0][axis] + SAFE_OVERLAP_MM
        end[axis] = second[1][axis] - SAFE_OVERLAP_MM
    return start, end


def main():
    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER)

    supports = []
    bands = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        item_role = role(name)
        if item_role is None or not rs.IsObjectSolid(object_id):
            continue
        box = bbox_min_max(object_id)
        if not box:
            continue
        item = (object_id, name, box)
        if item_role == "BASKET_SUPPORT":
            supports.append(item)
        elif item_role == "RING_BAND":
            bands.append(item)

    created = []
    skipped = []
    for support, band in itertools.product(supports, bands):
        support_id, support_name, support_box = support
        band_id, band_name, band_box = band
        separation = separated_axis(support_box, band_box)
        if separation is None:
            skipped.append({"support": support_name, "band": band_name, "reason": "NO_BBOX_GAP"})
            continue
        gap_mm, axis, direction = separation
        if not (0.05 < gap_mm <= MAX_TRIAL_GAP_MM):
            skipped.append({"support": support_name, "band": band_name, "reason": "GAP_OUTSIDE_TRIAL_RANGE", "gap_mm": round(gap_mm, 6)})
            continue

        start, end = bridge_points(support_box, band_box, axis, direction)
        bridge_id = rs.AddCylinder(start, end, BRIDGE_RADIUS_MM, cap=True)
        if not bridge_id:
            skipped.append({"support": support_name, "band": band_name, "reason": "ADD_CYLINDER_FAILED"})
            continue
        bridge_name = "PTR_BRIDGE_TRIAL_{0}_TO_{1}".format(support_name, band_name)
        rs.ObjectName(bridge_id, bridge_name)
        rs.ObjectLayer(bridge_id, TRIAL_LAYER)
        rs.ObjectColor(bridge_id, (255, 128, 0))
        created.append({
            "bridge_id": str(bridge_id),
            "bridge_name": bridge_name,
            "support_id": str(support_id),
            "band_id": str(band_id),
            "gap_mm": round(gap_mm, 6),
            "axis": ("X", "Y", "Z")[axis],
            "direction": "POSITIVE" if direction > 0 else "NEGATIVE",
            "safe_overlap_each_end_mm": SAFE_OVERLAP_MM,
            "bridge_radius_mm": BRIDGE_RADIUS_MM,
            "bridge_span_mm": round(gap_mm + (2.0 * SAFE_OVERLAP_MM), 6),
        })

    report = {
        "generator": "ptr-safe-metal-bridge-trial-v1",
        "status": "BRIDGE_TRIAL_CREATED" if created else "BRIDGE_TRIAL_NOT_CREATED",
        "trial_layer": TRIAL_LAYER,
        "created": created,
        "skipped": skipped,
        "original_geometry_modified": False,
        "original_geometry_deleted": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "warning": "Preview cylinders are not production-ready connection geometry.",
    }
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("SAFE METAL BRIDGE TRIAL | status=" + report["status"])
    for item in created:
        print("BRIDGE TRIAL | {0} | gap_mm={1:.3f} | axis={2} | direction={3} | span_mm={4:.3f} | radius_mm={5:.3f}".format(
            item["bridge_name"], item["gap_mm"], item["axis"], item["direction"],
            item["bridge_span_mm"], item["bridge_radius_mm"]))
    for item in skipped:
        print("SKIPPED | {0} -> {1} | {2}".format(item["support"], item["band"], item["reason"]))
    print("TRIAL LAYER | " + TRIAL_LAYER)
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("BRIDGE TRIAL REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_safe_metal_bridge_trial_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_safe_metal_bridge_trial(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_safe_metal_bridge_trial.py"
    report_path = memory_root / "Metal_Bridge_Trials" / f"{timestamp}_safe_metal_bridge_trial.json"
    return script_path, report_path, build_safe_metal_bridge_trial_script(report_path)


def save_safe_metal_bridge_trial(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
