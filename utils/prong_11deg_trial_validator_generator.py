"""Generate a report-only Rhino 8 Prong 11 Degree Trial Validator."""

from datetime import datetime
import json
from pathlib import Path

TARGET_TILT_DEG = 11.0
TILT_TOLERANCE_DEG = 0.25
MIN_ENGAGEMENT_RATIO = 0.25
MAX_SYMMETRY_SPREAD_DEG = 0.50


def classify_prong_trial(
    closed: bool,
    outward: bool,
    tilt_deg: float,
    engagement_ratio: float,
    stone_intersects: bool,
) -> str:
    if not closed:
        return "INVALID_TRIAL_SOLID"
    if not outward:
        return "TILTS_INWARD"
    if abs(tilt_deg - TARGET_TILT_DEG) > TILT_TOLERANCE_DEG:
        return "TILT_OUT_OF_TOLERANCE"
    if engagement_ratio < MIN_ENGAGEMENT_RATIO:
        return "ENGAGEMENT_TOO_SHALLOW"
    if stone_intersects:
        return "STONE_LOADING_COLLISION"
    return "READY_FOR_REPOSITION_REHEARSAL"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Prong 11 Degree Trial Validator
# REPORT ONLY: never moves, rotates, deletes, Booleans, or exports geometry.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
TARGET_TILT_DEG = 11.0
TILT_TOLERANCE_DEG = 0.25
MIN_ENGAGEMENT_RATIO = 0.25
MAX_SYMMETRY_SPREAD_DEG = 0.50
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj = sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None


def mesh_for(brep):
    pieces = Rhino.Geometry.Mesh.CreateFromBrep(
        brep, Rhino.Geometry.MeshingParameters.FastRenderMesh
    )
    mesh = Rhino.Geometry.Mesh()
    for piece in pieces or []:
        mesh.Append(piece)
    mesh.Compact()
    return mesh if mesh.Vertices.Count else None


def points_of(mesh):
    return [Rhino.Geometry.Point3d(vertex) for vertex in mesh.Vertices]


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
        values = (point.X-center.X, point.Y-center.Y, point.Z-center.Z)
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
        vector = [value / length for value in result]
    axis = Rhino.Geometry.Vector3d(*vector)
    if axis.Z < 0:
        axis.Reverse()
    return center, axis


def bbox_points(object_id):
    return list(rs.BoundingBox(object_id) or [])


def projection_interval(points, axis):
    values = [
        point.X * axis.X + point.Y * axis.Y + point.Z * axis.Z
        for point in points
    ]
    return min(values), max(values)


def overlap_depth(first_points, second_points, axis):
    first = projection_interval(first_points, axis)
    second = projection_interval(second_points, axis)
    return max(0.0, min(first[1], second[1]) - max(first[0], second[0]))


def estimated_diameter(object_id):
    corners = bbox_points(object_id)
    dimensions = sorted(
        max((point.X, point.Y, point.Z)[axis] for point in corners)
        - min((point.X, point.Y, point.Z)[axis] for point in corners)
        for axis in range(3)
    )
    return (dimensions[0] + dimensions[1]) / 2.0


def intersects(first, second):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(
            first, second, MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def status_for(closed, outward, tilt, engagement_ratio, stone_hit):
    if not closed:
        return "INVALID_TRIAL_SOLID"
    if not outward:
        return "TILTS_INWARD"
    if abs(tilt-TARGET_TILT_DEG) > TILT_TOLERANCE_DEG:
        return "TILT_OUT_OF_TOLERANCE"
    if engagement_ratio < MIN_ENGAGEMENT_RATIO:
        return "ENGAGEMENT_TOO_SHALLOW"
    if stone_hit:
        return "STONE_LOADING_COLLISION"
    return "READY_FOR_REPOSITION_REHEARSAL"


def main():
    seat_id = None
    stone_id = None
    trial_ids = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        upper = name.upper()
        if upper.endswith("_11DEG_REPOSITION_COPY"):
            trial_ids.append(object_id)
        elif "STONE_SEAT" in upper and not any(
            marker in upper for marker in ("TRIAL", "COPY", "REHEARSAL", "RESULT")
        ):
            seat_id = object_id
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper and "TRIAL" not in upper
        ):
            stone_id = object_id

    blockers = []
    if seat_id is None:
        blockers.append("One original Stone Seat is required.")
    if len(trial_ids) != 4:
        blockers.append("Four 11-degree trial Prongs are required.")

    seat_brep = brep_for(seat_id) if seat_id else None
    seat_mesh = mesh_for(seat_brep) if seat_brep else None
    seat_center = centroid(points_of(seat_mesh)) if seat_mesh else None
    stone_brep = brep_for(stone_id) if stone_id else None

    results = []
    if not blockers:
        for trial_id in trial_ids:
            name = object_name(trial_id)
            brep = brep_for(trial_id)
            mesh = mesh_for(brep) if brep else None
            center, axis = principal_axis(points_of(mesh))
            tilt = math.degrees(math.acos(max(-1.0, min(1.0, axis.Z))))

            outward_axis = Rhino.Geometry.Vector3d(
                center.X-seat_center.X, center.Y-seat_center.Y, 0.0
            )
            radial_ok = outward_axis.Unitize()
            outward_dot = (
                axis.X*outward_axis.X + axis.Y*outward_axis.Y
                if radial_ok else -1.0
            )
            outward = bool(radial_ok and outward_dot > 0.0)

            diameter = estimated_diameter(trial_id)
            engagement_depth = overlap_depth(
                bbox_points(trial_id), bbox_points(seat_id), outward_axis
            ) if radial_ok else 0.0
            engagement_ratio = engagement_depth / diameter if diameter else 0.0
            seat_hit = intersects(brep, seat_brep)
            stone_hit = intersects(brep, stone_brep) if stone_brep else False
            status = status_for(
                bool(rs.IsObjectSolid(trial_id)),
                outward,
                tilt,
                engagement_ratio,
                stone_hit,
            )
            if not seat_hit and status == "READY_FOR_REPOSITION_REHEARSAL":
                status = "NO_SEAT_SURFACE_INTERSECTION"

            results.append({
                "trial_id": str(trial_id),
                "trial_name": name,
                "status": status,
                "closed_solid": bool(rs.IsObjectSolid(trial_id)),
                "tilt_deg": round(tilt, 6),
                "outward": outward,
                "outward_dot": round(outward_dot, 6),
                "estimated_diameter_mm": round(diameter, 6),
                "engagement_depth_mm": round(engagement_depth, 6),
                "engagement_ratio": round(engagement_ratio, 6),
                "minimum_required_engagement_mm": round(diameter*MIN_ENGAGEMENT_RATIO, 6),
                "seat_surface_intersection": seat_hit,
                "stone_loading_collision": stone_hit,
            })

    tilts = [item["tilt_deg"] for item in results]
    symmetry_spread = max(tilts)-min(tilts) if tilts else 0.0
    symmetry_ok = bool(tilts and symmetry_spread <= MAX_SYMMETRY_SPREAD_DEG)
    ready_count = sum(
        item["status"] == "READY_FOR_REPOSITION_REHEARSAL" for item in results
    )
    report_status = (
        "PRONG_11DEG_TRIAL_READY"
        if ready_count == 4 and symmetry_ok and not blockers
        else "PRONG_11DEG_TRIAL_REVIEW_REQUIRED"
    )
    report = {
        "generator": "ptr-prong-11deg-trial-validator-v1",
        "status": report_status,
        "trial_count": len(trial_ids),
        "ready_count": ready_count,
        "target_tilt_deg": TARGET_TILT_DEG,
        "tilt_tolerance_deg": TILT_TOLERANCE_DEG,
        "minimum_engagement_ratio": MIN_ENGAGEMENT_RATIO,
        "symmetry_spread_deg": round(symmetry_spread, 6),
        "symmetry_ok": symmetry_ok,
        "stone_present": stone_brep is not None,
        "results": results,
        "blockers": blockers,
        "geometry_modified": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "warning": "Engagement depth uses projected bounding boxes; inspect real Rhino surfaces before production.",
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("PRONG 11DEG TRIAL VALIDATOR | status="+report_status)
    print("TRIAL PRONGS | count={0} | ready={1} | symmetry_spread_deg={2:.3f}".format(
        len(trial_ids), ready_count, symmetry_spread
    ))
    for item in results:
        print("PRONG VALIDATION | {0} | {1} | tilt_deg={2:.3f} | outward={3} | engagement_mm={4:.3f} | engagement_ratio={5:.3f} | seat_intersection={6} | stone_collision={7}".format(
            item["trial_name"], item["status"], item["tilt_deg"], item["outward"],
            item["engagement_depth_mm"], item["engagement_ratio"],
            item["seat_surface_intersection"], item["stone_loading_collision"]
        ))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PRONG VALIDATION REPORT | "+REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_prong_11deg_trial_validator_script(report_path: Path) -> str:
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/"))
    )


def prepare_prong_11deg_trial_validator(memory_root: Path, now: datetime | None = None):
    stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_prong_11deg_trial_validator.py"
    report_path = memory_root / "Prong_11Deg_Validation" / f"{stamp}_prong_11deg_trial_validator.json"
    return script_path, report_path, build_prong_11deg_trial_validator_script(report_path)


def save_prong_11deg_trial_validator(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
