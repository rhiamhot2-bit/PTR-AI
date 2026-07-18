"""Generate a report-only Rhino 8 Upper Contact Distance Analyzer."""

from datetime import datetime
import json
from pathlib import Path

SAFE_OVERLAP_MM = 0.15
MAX_SIMPLE_EXTENSION_MM = 1.50


def classify_surface_gap(gap_mm: float) -> str:
    if gap_mm <= 0.05:
        return "VERIFY_NEAR_CONTACT"
    if gap_mm <= MAX_SIMPLE_EXTENSION_MM:
        return "EXTENSION_CANDIDATE"
    return "NEW_CONNECTION_GEOMETRY_REQUIRED"


def proposed_extension_mm(gap_mm: float) -> float:
    return round(max(0.0, gap_mm) + SAFE_OVERLAP_MM, 3)


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Upper Contact Distance Analyzer
# REPORT ONLY: temporary meshes remain in memory and are never added to the document.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
SAFE_OVERLAP_MM = 0.15
MAX_SIMPLE_EXTENSION_MM = 1.50


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


def role(name):
    value = name.upper()
    if any(marker in value for marker in (
        "REHEARSAL", "TRIAL", "COPY", "RESULT", "STONE_PLACEHOLDER", "GIRDLE_GUIDE"
    )):
        return None
    if "STONE_SEAT" in value:
        return "SEAT"
    if "PRONG" in value:
        return "PRONG"
    if "BASKET_SUPPORT" in value:
        return "SUPPORT"
    return None


def mesh_for(brep):
    pieces = Rhino.Geometry.Mesh.CreateFromBrep(
        brep, Rhino.Geometry.MeshingParameters.FastRenderMesh
    )
    if not pieces:
        return None
    combined = Rhino.Geometry.Mesh()
    for piece in pieces:
        combined.Append(piece)
    combined.Normals.ComputeNormals()
    combined.Compact()
    return combined


def closest_point(mesh, point):
    try:
        mesh_point = mesh.ClosestMeshPoint(point, 0.0)
        return mesh_point.Point if mesh_point else None
    except Exception:
        try:
            result = mesh.ClosestPoint(point)
            return result if result and result.IsValid else None
        except Exception:
            return None


def closest_mesh_pair(target_mesh, seat_mesh):
    best = None

    for vertex in target_mesh.Vertices:
        target_point = Rhino.Geometry.Point3d(vertex)
        seat_point = closest_point(seat_mesh, target_point)
        if seat_point is None:
            continue
        distance = target_point.DistanceTo(seat_point)
        if best is None or distance < best[0]:
            best = (distance, target_point, seat_point)

    for vertex in seat_mesh.Vertices:
        seat_point = Rhino.Geometry.Point3d(vertex)
        target_point = closest_point(target_mesh, seat_point)
        if target_point is None:
            continue
        distance = target_point.DistanceTo(seat_point)
        if best is None or distance < best[0]:
            best = (distance, target_point, seat_point)

    return best


def classify(gap_mm):
    if gap_mm <= 0.05:
        return "VERIFY_NEAR_CONTACT"
    if gap_mm <= MAX_SIMPLE_EXTENSION_MM:
        return "EXTENSION_CANDIDATE"
    return "NEW_CONNECTION_GEOMETRY_REQUIRED"


def main():
    seat = None
    targets = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        item_role = role(name)
        if item_role is None:
            continue
        brep = brep_for(object_id)
        if brep is None or not rs.IsObjectSolid(object_id):
            continue
        item = {"id": object_id, "name": name, "role": item_role, "brep": brep}
        if item_role == "SEAT":
            seat = item
        else:
            targets.append(item)

    blockers = []
    if seat is None:
        blockers.append("Exactly one valid original Stone Seat is required.")
    if len([item for item in targets if item["role"] == "PRONG"]) != 4:
        blockers.append("Exactly four valid original Prongs are required.")
    if len([item for item in targets if item["role"] == "SUPPORT"]) != 2:
        blockers.append("Exactly two valid original Basket Supports are required.")

    results = []
    if not blockers:
        seat_mesh = mesh_for(seat["brep"])
        if seat_mesh is None:
            blockers.append("Stone Seat temporary mesh creation failed.")
        else:
            for target in targets:
                target_mesh = mesh_for(target["brep"])
                pair = closest_mesh_pair(target_mesh, seat_mesh) if target_mesh else None
                if pair is None:
                    results.append({
                        "target_name": target["name"],
                        "target_role": target["role"],
                        "status": "DISTANCE_MEASUREMENT_FAILED",
                    })
                    continue

                gap, target_point, seat_point = pair
                vector = seat_point - target_point
                length = vector.Length
                if length > 0:
                    vector.Unitize()
                status = classify(gap)
                results.append({
                    "seat_id": str(seat["id"]),
                    "seat_name": seat["name"],
                    "target_id": str(target["id"]),
                    "target_name": target["name"],
                    "target_role": target["role"],
                    "status": status,
                    "surface_gap_mm": round(gap, 6),
                    "point_on_target": [round(target_point.X, 6), round(target_point.Y, 6), round(target_point.Z, 6)],
                    "point_on_seat": [round(seat_point.X, 6), round(seat_point.Y, 6), round(seat_point.Z, 6)],
                    "direction_target_toward_seat": {
                        "x": round(vector.X, 6) if length > 0 else 0.0,
                        "y": round(vector.Y, 6) if length > 0 else 0.0,
                        "z": round(vector.Z, 6) if length > 0 else 0.0,
                    },
                    "safe_overlap_mm": SAFE_OVERLAP_MM,
                    "proposed_extension_mm": (
                        round(gap + SAFE_OVERLAP_MM, 6)
                        if status == "EXTENSION_CANDIDATE" else None
                    ),
                })

    report = {
        "generator": "ptr-upper-contact-distance-analyzer-v1",
        "status": "UPPER_CONTACT_DISTANCE_REVIEW_REQUIRED" if not blockers else "UPPER_CONTACT_DISTANCE_BLOCKED",
        "method": "two-way temporary mesh closest-surface sampling estimate",
        "pair_count": len(results),
        "safe_overlap_mm": SAFE_OVERLAP_MM,
        "results": results,
        "blockers": blockers,
        "geometry_modified": False,
        "temporary_meshes_added_to_document": False,
        "production_export_allowed": False,
        "warning": "Mesh sampling is an estimate; verify dimensions with Rhino inspection tools.",
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("UPPER CONTACT DISTANCE ANALYZER | status=" + report["status"])
    print("UPPER DISTANCES | count={0}".format(len(results)))
    for item in results:
        if "surface_gap_mm" not in item:
            print("DISTANCE | {0} | {1}".format(item["target_name"], item["status"]))
            continue
        direction = item["direction_target_toward_seat"]
        print("DISTANCE | {0} -> {1} | {2} | gap_mm={3:.3f} | vector=({4:.3f},{5:.3f},{6:.3f}) | extension_mm={7}".format(
            item["target_name"], item["seat_name"], item["status"],
            item["surface_gap_mm"], direction["x"], direction["y"], direction["z"],
            item["proposed_extension_mm"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("TEMPORARY MESHES ADDED TO DOCUMENT | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("UPPER DISTANCE REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_upper_contact_distance_analyzer_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_upper_contact_distance_analyzer(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_upper_contact_distances.py"
    report_path = memory_root / "Upper_Contact_Distances" / f"{timestamp}_upper_contact_distances.json"
    return script_path, report_path, build_upper_contact_distance_analyzer_script(report_path)


def save_upper_contact_distance_analyzer(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
