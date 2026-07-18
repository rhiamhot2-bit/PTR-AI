"""Generate a Rhino 8 preview-only Upper Contact Bridge Trial."""

from datetime import datetime
import json
from pathlib import Path

SAFE_OVERLAP_MM = 0.15
PRONG_BRIDGE_RADIUS_MM = 0.30
SUPPORT_BRIDGE_RADIUS_MM = 0.45


def upper_bridge_span_mm(gap_mm: float) -> float:
    return round(max(0.0, gap_mm) + (2 * SAFE_OVERLAP_MM), 3)


def upper_bridge_radius_mm(role: str) -> float:
    return PRONG_BRIDGE_RADIUS_MM if role == "PRONG" else SUPPORT_BRIDGE_RADIUS_MM


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Upper Contact Bridge Trial
# PREVIEW ONLY: adds trial connectors; original geometry is never moved or Booleaned.
import io
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
TRIAL_LAYER = "PTR_UPPER_CONTACT_BRIDGE_TRIAL"
SAFE_OVERLAP_MM = 0.15
MAX_TRIAL_GAP_MM = 1.50
PRONG_BRIDGE_RADIUS_MM = 0.30
SUPPORT_BRIDGE_RADIUS_MM = 0.45


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


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


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


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
            return mesh.ClosestPoint(point)
        except Exception:
            return None


def closest_pair(target_mesh, seat_mesh):
    best = None
    for vertex in target_mesh.Vertices:
        target_point = Rhino.Geometry.Point3d(vertex)
        seat_point = closest_point(seat_mesh, target_point)
        if seat_point is not None:
            distance = target_point.DistanceTo(seat_point)
            if best is None or distance < best[0]:
                best = (distance, target_point, seat_point)
    for vertex in seat_mesh.Vertices:
        seat_point = Rhino.Geometry.Point3d(vertex)
        target_point = closest_point(target_mesh, seat_point)
        if target_point is not None:
            distance = target_point.DistanceTo(seat_point)
            if best is None or distance < best[0]:
                best = (distance, target_point, seat_point)
    return best


def main():
    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER)

    seat = None
    targets = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        item_role = role(name)
        if item_role is None or not rs.IsObjectSolid(object_id):
            continue
        brep = brep_for(object_id)
        if brep is None:
            continue
        item = {"id": object_id, "name": name, "role": item_role, "brep": brep}
        if item_role == "SEAT":
            seat = item
        else:
            targets.append(item)

    blockers = []
    if seat is None:
        blockers.append("One valid original Stone Seat is required.")
    if len([item for item in targets if item["role"] == "PRONG"]) != 4:
        blockers.append("Four valid original Prongs are required.")
    if len([item for item in targets if item["role"] == "SUPPORT"]) != 2:
        blockers.append("Two valid original Basket Supports are required.")

    created = []
    skipped = []
    if not blockers:
        seat_mesh = mesh_for(seat["brep"])
        for target in targets:
            target_mesh = mesh_for(target["brep"])
            pair = closest_pair(target_mesh, seat_mesh) if target_mesh and seat_mesh else None
            if pair is None:
                skipped.append({"target": target["name"], "reason": "DISTANCE_FAILED"})
                continue
            gap, target_point, seat_point = pair
            if gap > MAX_TRIAL_GAP_MM:
                skipped.append({"target": target["name"], "reason": "GAP_OUTSIDE_TRIAL_RANGE", "gap_mm": round(gap, 6)})
                continue

            direction = seat_point - target_point
            if direction.Length <= 0:
                skipped.append({"target": target["name"], "reason": "ZERO_LENGTH_DIRECTION"})
                continue
            direction.Unitize()
            start = target_point - (direction * SAFE_OVERLAP_MM)
            end = seat_point + (direction * SAFE_OVERLAP_MM)
            radius = PRONG_BRIDGE_RADIUS_MM if target["role"] == "PRONG" else SUPPORT_BRIDGE_RADIUS_MM
            bridge_id = rs.AddCylinder(start, end, radius, cap=True)
            if not bridge_id:
                skipped.append({"target": target["name"], "reason": "ADD_CYLINDER_FAILED"})
                continue

            bridge_name = "PTR_UPPER_BRIDGE_TRIAL_{0}_TO_{1}".format(target["name"], seat["name"])
            rs.ObjectName(bridge_id, bridge_name)
            rs.ObjectLayer(bridge_id, TRIAL_LAYER)
            rs.ObjectColor(bridge_id, (255, 0, 180))
            created.append({
                "bridge_id": str(bridge_id),
                "bridge_name": bridge_name,
                "target_id": str(target["id"]),
                "seat_id": str(seat["id"]),
                "target_role": target["role"],
                "gap_mm": round(gap, 6),
                "span_mm": round(gap + (2 * SAFE_OVERLAP_MM), 6),
                "radius_mm": radius,
                "safe_overlap_each_end_mm": SAFE_OVERLAP_MM,
                "direction_target_toward_seat": {
                    "x": round(direction.X, 6),
                    "y": round(direction.Y, 6),
                    "z": round(direction.Z, 6),
                },
            })

    report = {
        "generator": "ptr-upper-contact-bridge-trial-v1",
        "status": "UPPER_BRIDGE_TRIAL_CREATED" if len(created) == 6 else "UPPER_BRIDGE_TRIAL_REVIEW_REQUIRED",
        "trial_layer": TRIAL_LAYER,
        "created_count": len(created),
        "created": created,
        "skipped": skipped,
        "blockers": blockers,
        "original_geometry_modified": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "warning": "Preview cylinders are not production-ready geometry.",
    }
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("UPPER CONTACT BRIDGE TRIAL | status=" + report["status"])
    print("UPPER BRIDGES | created={0} | skipped={1}".format(len(created), len(skipped)))
    for item in created:
        vector = item["direction_target_toward_seat"]
        print("UPPER BRIDGE | {0} | role={1} | gap_mm={2:.3f} | span_mm={3:.3f} | radius_mm={4:.3f} | vector=({5:.3f},{6:.3f},{7:.3f})".format(
            item["bridge_name"], item["target_role"], item["gap_mm"], item["span_mm"],
            item["radius_mm"], vector["x"], vector["y"], vector["z"]))
    for item in skipped:
        print("SKIPPED | {0} | {1}".format(item["target"], item["reason"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("TRIAL LAYER | " + TRIAL_LAYER)
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("UPPER BRIDGE REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_upper_contact_bridge_trial_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_upper_contact_bridge_trial(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_upper_contact_bridge_trial.py"
    report_path = memory_root / "Upper_Contact_Bridge_Trials" / f"{timestamp}_upper_contact_bridge_trial.json"
    return script_path, report_path, build_upper_contact_bridge_trial_script(report_path)


def save_upper_contact_bridge_trial(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
