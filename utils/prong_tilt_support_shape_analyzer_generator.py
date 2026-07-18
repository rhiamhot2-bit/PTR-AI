"""Generate a report-only Prong Tilt and Support Shape Analyzer."""

from datetime import datetime
import json
from pathlib import Path

TARGET_PRONG_TILT_DEG = 11.0
SUPPORT_STRAIGHTNESS_TOLERANCE_MM = 0.08


def tilt_adjustment_deg(current_deg: float) -> float:
    return round(TARGET_PRONG_TILT_DEG - current_deg, 3)


def support_shape(max_deviation_mm: float) -> str:
    return "STRAIGHT" if max_deviation_mm <= SUPPORT_STRAIGHTNESS_TOLERANCE_MM else "CURVED"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Current Prong Tilt & Support Shape Analyzer
# REPORT ONLY: temporary meshes remain in memory.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
TARGET_PRONG_TILT_DEG = 11.0
SUPPORT_STRAIGHTNESS_TOLERANCE_MM = 0.08


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def role(name):
    value = name.upper()
    if any(marker in value for marker in ("REHEARSAL", "TRIAL", "COPY", "RESULT")):
        return None
    if "PRONG" in value:
        return "PRONG"
    if "BASKET_SUPPORT" in value:
        return "SUPPORT"
    return None


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


def mesh_vertices(brep):
    pieces = Rhino.Geometry.Mesh.CreateFromBrep(
        brep, Rhino.Geometry.MeshingParameters.FastRenderMesh
    )
    points = []
    for piece in pieces or []:
        for vertex in piece.Vertices:
            points.append(Rhino.Geometry.Point3d(vertex))
    return points


def centroid(points):
    count = float(len(points))
    return Rhino.Geometry.Point3d(
        sum(point.X for point in points) / count,
        sum(point.Y for point in points) / count,
        sum(point.Z for point in points) / count,
    )


def principal_axis(points):
    center = centroid(points)
    covariance = [[0.0] * 3 for _ in range(3)]
    for point in points:
        values = (point.X - center.X, point.Y - center.Y, point.Z - center.Z)
        for row in range(3):
            for column in range(3):
                covariance[row][column] += values[row] * values[column]

    vector = [0.371, 0.557, 0.743]
    for _ in range(32):
        result = [
            sum(covariance[row][column] * vector[column] for column in range(3))
            for row in range(3)
        ]
        length = math.sqrt(sum(value * value for value in result))
        if length <= 1e-12:
            return center, Rhino.Geometry.Vector3d.ZAxis
        vector = [value / length for value in result]
    axis = Rhino.Geometry.Vector3d(vector[0], vector[1], vector[2])
    if axis.Z < 0:
        axis.Reverse()
    return center, axis


def projection(point, center, axis):
    return Rhino.Geometry.Vector3d.Multiply(point - center, axis)


def support_centerline_analysis(points, center, axis):
    samples = [(projection(point, center, axis), point) for point in points]
    low = min(item[0] for item in samples)
    high = max(item[0] for item in samples)
    bin_count = 7
    width = (high - low) / float(bin_count) if high > low else 1.0
    deviations = []
    for index in range(bin_count):
        start = low + (index * width)
        end = high if index == bin_count - 1 else start + width
        bin_points = [point for value, point in samples if start <= value <= end]
        if not bin_points:
            continue
        bin_center = centroid(bin_points)
        average_t = sum(projection(point, center, axis) for point in bin_points) / float(len(bin_points))
        line_point = center + (axis * average_t)
        deviations.append(bin_center.DistanceTo(line_point))

    bottom = center + (axis * low)
    top = center + (axis * high)
    return max(deviations) if deviations else 0.0, bottom, top


def main():
    prongs = []
    supports = []
    blockers = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        item_role = role(name)
        if item_role is None or not rs.IsObjectSolid(object_id):
            continue
        brep = brep_for(object_id)
        points = mesh_vertices(brep) if brep else []
        if len(points) < 4:
            blockers.append("Mesh analysis failed: " + name)
            continue
        center, axis = principal_axis(points)
        if item_role == "PRONG":
            current_tilt = math.degrees(math.acos(max(-1.0, min(1.0, abs(axis.Z)))))
            prongs.append({
                "id": str(object_id),
                "name": name,
                "axis": {"x": round(axis.X, 6), "y": round(axis.Y, 6), "z": round(axis.Z, 6)},
                "current_tilt_deg": round(current_tilt, 6),
                "target_tilt_deg": TARGET_PRONG_TILT_DEG,
                "adjustment_deg": round(TARGET_PRONG_TILT_DEG - current_tilt, 6),
            })
        else:
            deviation, bottom, top = support_centerline_analysis(points, center, axis)
            supports.append({
                "id": str(object_id),
                "name": name,
                "axis": {"x": round(axis.X, 6), "y": round(axis.Y, 6), "z": round(axis.Z, 6)},
                "current_shape": "STRAIGHT" if deviation <= SUPPORT_STRAIGHTNESS_TOLERANCE_MM else "CURVED",
                "centerline_max_deviation_mm": round(deviation, 6),
                "bottom_center_estimate": [round(bottom.X, 6), round(bottom.Y, 6), round(bottom.Z, 6)],
                "top_center_estimate": [round(top.X, 6), round(top.Y, 6), round(top.Z, 6)],
                "target_shape": "CURVED_SYMMETRIC",
                "top_contact_target": "100_PERCENT_STONE_SEAT",
                "bottom_contact_target": "100_PERCENT_RING_BAND",
            })

    if len(prongs) != 4:
        blockers.append("Exactly four original Prongs are required.")
    if len(supports) != 2:
        blockers.append("Exactly two original Basket Supports are required.")

    tilts = [item["current_tilt_deg"] for item in prongs]
    spread = max(tilts) - min(tilts) if tilts else None
    report = {
        "generator": "ptr-prong-tilt-support-shape-analyzer-v1",
        "status": "TILT_SHAPE_REVIEW_REQUIRED" if not blockers else "TILT_SHAPE_BLOCKED",
        "prongs": prongs,
        "supports": supports,
        "prong_tilt_spread_deg": round(spread, 6) if spread is not None else None,
        "prong_symmetry_within_1_deg": bool(spread is not None and spread <= 1.0),
        "blockers": blockers,
        "geometry_modified": False,
        "temporary_meshes_added_to_document": False,
        "production_export_allowed": False,
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("PRONG TILT & SUPPORT SHAPE ANALYZER | status=" + report["status"])
    for item in prongs:
        print("PRONG TILT | {0} | current_deg={1:.3f} | target_deg=11.000 | adjustment_deg={2:.3f} | axis=({3:.3f},{4:.3f},{5:.3f})".format(
            item["name"], item["current_tilt_deg"], item["adjustment_deg"],
            item["axis"]["x"], item["axis"]["y"], item["axis"]["z"]))
    print("PRONG SYMMETRY | spread_deg={0} | within_1_deg={1}".format(
        report["prong_tilt_spread_deg"], report["prong_symmetry_within_1_deg"]))
    for item in supports:
        print("SUPPORT SHAPE | {0} | current={1} | centerline_deviation_mm={2:.3f} | target=CURVED_SYMMETRIC".format(
            item["name"], item["current_shape"], item["centerline_max_deviation_mm"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("TEMPORARY MESHES ADDED TO DOCUMENT | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("TILT SHAPE REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_prong_tilt_support_shape_analyzer_script(report_path: Path) -> str:
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/")))


def prepare_prong_tilt_support_shape_analyzer(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_prong_tilt_support_shape.py"
    report_path = memory_root / "Prong_Tilt_Support_Shape" / f"{timestamp}_prong_tilt_support_shape.json"
    return script_path, report_path, build_prong_tilt_support_shape_analyzer_script(report_path)


def save_prong_tilt_support_shape_analyzer(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
