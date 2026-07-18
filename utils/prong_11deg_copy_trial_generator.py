"""Generate a copy-only Rhino 8 Prong 11° Reposition Trial."""

from datetime import datetime
import json
from pathlib import Path

TARGET_TILT_DEG = 11.0
MIN_ENGAGEMENT_RATIO = 0.25


def additional_tilt_deg(current_tilt_deg: float) -> float:
    return round(TARGET_TILT_DEG - current_tilt_deg, 3)


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Prong 11 Degree Copy Reposition Trial
# COPY ONLY: original Prongs and Stone Seat are never transformed.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
TRIAL_LAYER = "PTR_PRONG_11DEG_REPOSITION_TRIAL"
TARGET_TILT_DEG = 11.0
MIN_ENGAGEMENT_RATIO = 0.25


def name_of(object_id):
    return rs.ObjectName(object_id) or ""


def original_role(name):
    value = name.upper()
    if any(marker in value for marker in ("REHEARSAL", "TRIAL", "COPY", "RESULT", "STONE_PLACEHOLDER")):
        return None
    if "STONE_SEAT" in value:
        return "SEAT"
    if "PRONG" in value:
        return "PRONG"
    return None


def brep_for(object_id):
    obj = sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None


def mesh_for(brep):
    pieces = Rhino.Geometry.Mesh.CreateFromBrep(brep, Rhino.Geometry.MeshingParameters.FastRenderMesh)
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
        sum(p.X for p in points) / count,
        sum(p.Y for p in points) / count,
        sum(p.Z for p in points) / count,
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
        result = [sum(covariance[row][column]*vector[column] for column in range(3)) for row in range(3)]
        length = math.sqrt(sum(value*value for value in result))
        vector = [value/length for value in result]
    axis = Rhino.Geometry.Vector3d(*vector)
    if axis.Z < 0:
        axis.Reverse()
    projections = [Rhino.Geometry.Vector3d.Multiply(point-center, axis) for point in points]
    bottom = center + (axis * min(projections))
    return center, axis, bottom


def estimated_diameter(object_id):
    corners = rs.BoundingBox(object_id)
    values = [(p.X,p.Y,p.Z) for p in corners]
    dimensions = sorted(
        max(p[i] for p in values)-min(p[i] for p in values) for i in range(3)
    )
    return (dimensions[0]+dimensions[1])/2.0


def closest_point(mesh, point):
    mesh_point = mesh.ClosestMeshPoint(point, 0.0)
    return mesh_point.Point if mesh_point else None


def closest_pair(target_mesh, seat_mesh):
    best = None
    for point in points_of(target_mesh):
        other = closest_point(seat_mesh, point)
        if other:
            distance = point.DistanceTo(other)
            if best is None or distance < best[0]:
                best = (distance, point, other)
    for point in points_of(seat_mesh):
        other = closest_point(target_mesh, point)
        if other:
            distance = point.DistanceTo(other)
            if best is None or distance < best[0]:
                best = (distance, other, point)
    return best


def main():
    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER)

    seat_id = None
    prong_ids = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        role = original_role(name_of(object_id))
        if role == "SEAT":
            seat_id = object_id
        elif role == "PRONG" and rs.IsObjectSolid(object_id):
            prong_ids.append(object_id)

    blockers = []
    if seat_id is None:
        blockers.append("One original Stone Seat is required.")
    if len(prong_ids) != 4:
        blockers.append("Four original Prongs are required.")

    records = []
    seat_mesh = mesh_for(brep_for(seat_id)) if seat_id else None
    seat_center = centroid(points_of(seat_mesh)) if seat_mesh else None
    if not blockers:
        for source_id in prong_ids:
            source_name = name_of(source_id)
            source_mesh = mesh_for(brep_for(source_id))
            points = points_of(source_mesh)
            center, current_axis, pivot = principal_axis(points)
            current_tilt = math.degrees(math.acos(max(-1.0,min(1.0,current_axis.Z))))
            # The sign matters: define OUTWARD from the Seat center to this Prong.
            # Reusing the current axis horizontal component can preserve or amplify
            # an inward lean even while the numeric tilt magnitude reaches 11 degrees.
            outward = Rhino.Geometry.Vector3d(
                center.X-seat_center.X,
                center.Y-seat_center.Y,
                0.0,
            )
            if not outward.Unitize():
                blockers.append(source_name+": cannot determine outward direction.")
                continue
            radians = math.radians(TARGET_TILT_DEG)
            desired_axis = Rhino.Geometry.Vector3d(
                outward.X*math.sin(radians),
                outward.Y*math.sin(radians),
                math.cos(radians),
            )
            rotation_axis = Rhino.Geometry.Vector3d.CrossProduct(current_axis,desired_axis)
            rotation_angle = math.degrees(Rhino.Geometry.Vector3d.VectorAngle(current_axis,desired_axis))
            if not rotation_axis.Unitize():
                rotation_axis = Rhino.Geometry.Vector3d.ZAxis

            copy_id = rs.CopyObject(source_id)
            rs.ObjectName(copy_id,source_name+"_11DEG_REPOSITION_COPY")
            rs.ObjectLayer(copy_id,TRIAL_LAYER)
            rs.ObjectColor(copy_id,(80,140,255))
            rs.RotateObject(copy_id,pivot,rotation_angle,rotation_axis,copy=False)

            copy_mesh = mesh_for(brep_for(copy_id))
            pair = closest_pair(copy_mesh,seat_mesh)
            gap,target_point,seat_point = pair
            direction = seat_point-target_point
            direction.Unitize()
            diameter = estimated_diameter(source_id)
            engagement = diameter*MIN_ENGAGEMENT_RATIO
            move_distance = gap+engagement
            movement = direction*move_distance
            rs.MoveObject(copy_id,movement)

            records.append({
                "source_id":str(source_id),
                "copy_id":str(copy_id),
                "source_name":source_name,
                "current_tilt_deg":round(current_tilt,6),
                "target_tilt_deg":TARGET_TILT_DEG,
                "rotation_applied_deg":round(rotation_angle,6),
                "direction_rule":"OUTWARD_FROM_SEAT_CENTER",
                "estimated_diameter_mm":round(diameter,6),
                "minimum_engagement_mm":round(engagement,6),
                "surface_gap_after_rotation_mm":round(gap,6),
                "translation_applied_mm":round(move_distance,6),
                "translation_vector":[round(movement.X,6),round(movement.Y,6),round(movement.Z,6)],
            })

    report = {
        "generator":"ptr-prong-11deg-copy-reposition-trial-v1",
        "status":"PRONG_11DEG_COPY_TRIAL_CREATED" if len(records)==4 else "PRONG_11DEG_COPY_TRIAL_BLOCKED",
        "trial_layer":TRIAL_LAYER,
        "records":records,
        "blockers":blockers,
        "original_geometry_modified":False,
        "boolean_executed":False,
        "production_export_allowed":False,
    }
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)

    print("PRONG 11DEG COPY REPOSITION TRIAL | status="+report["status"])
    for item in records:
        print("PRONG COPY | {0} | current={1:.3f} | rotation={2:.3f} | target=11.000 | engagement_mm={3:.3f} | translation_mm={4:.3f}".format(
            item["source_name"],item["current_tilt_deg"],item["rotation_applied_deg"],
            item["minimum_engagement_mm"],item["translation_applied_mm"]))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PRONG TRIAL REPORT | "+REPORT_PATH)


if __name__=="__main__":
    main()
'''


def build_prong_11deg_copy_trial_script(report_path: Path) -> str:
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__",json.dumps(str(report_path).replace("\\","/")))


def prepare_prong_11deg_copy_trial(memory_root: Path, now: datetime | None=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_prong_11deg_copy_trial.py"
    report_path=memory_root/"Prong_11Deg_Copy_Trials"/f"{stamp}_prong_11deg_copy_trial.json"
    return script_path,report_path,build_prong_11deg_copy_trial_script(report_path)


def save_prong_11deg_copy_trial(script_path: Path,script: str)->None:
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
