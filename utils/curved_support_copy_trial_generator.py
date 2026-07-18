"""Generate a copy-only Rhino 8 Curved Support Trial."""

from datetime import datetime
import json
from pathlib import Path

CONTACT_OVERLAP_MM = 0.20
BOW_RATIO = 0.60


def trial_status(support_count: int, created_count: int) -> str:
    if support_count != 2:
        return "CURVED_SUPPORT_TRIAL_BLOCKED"
    if created_count != 2:
        return "CURVED_SUPPORT_TRIAL_INCOMPLETE"
    return "CURVED_SUPPORT_TRIAL_CREATED"


_SCRIPT_TEMPLATE=r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Curved Support Copy Trial
# Creates new curved trial supports; original supports are never edited or deleted.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing

REPORT_PATH=__REPORT_PATH__
TRIAL_LAYER="PTR_CURVED_SUPPORT_COPY_TRIAL"
CONTACT_OVERLAP_MM=0.20
BOW_RATIO=0.60
MODEL_TOLERANCE=float(sc.doc.ModelAbsoluteTolerance)
ANGLE_TOLERANCE=float(sc.doc.ModelAngleToleranceRadians)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj=sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry,Rhino.Geometry.Brep) else None


def mesh_for(brep):
    pieces=Rhino.Geometry.Mesh.CreateFromBrep(
        brep,Rhino.Geometry.MeshingParameters.FastRenderMesh
    )
    mesh=Rhino.Geometry.Mesh()
    for piece in pieces or []:
        mesh.Append(piece)
    mesh.Compact()
    return mesh if mesh.Vertices.Count else None


def points_of(mesh):
    return [Rhino.Geometry.Point3d(vertex) for vertex in mesh.Vertices]


def centroid(points):
    count=float(len(points))
    return Rhino.Geometry.Point3d(
        sum(point.X for point in points)/count,
        sum(point.Y for point in points)/count,
        sum(point.Z for point in points)/count,
    )


def principal_endpoints(points):
    center=centroid(points)
    covariance=[[0.0]*3 for _ in range(3)]
    for point in points:
        values=(point.X-center.X,point.Y-center.Y,point.Z-center.Z)
        for row in range(3):
            for column in range(3):
                covariance[row][column]+=values[row]*values[column]
    vector=[0.371,0.557,0.743]
    for _ in range(32):
        result=[
            sum(covariance[row][column]*vector[column] for column in range(3))
            for row in range(3)
        ]
        length=math.sqrt(sum(value*value for value in result))
        vector=[value/length for value in result]
    axis=Rhino.Geometry.Vector3d(*vector)
    if axis.Z<0:
        axis.Reverse()
    projections=[Rhino.Geometry.Vector3d.Multiply(point-center,axis) for point in points]
    bottom=center+(axis*min(projections))
    top=center+(axis*max(projections))
    return center,bottom,top


def estimated_diameter(object_id):
    corners=list(rs.BoundingBox(object_id) or [])
    dimensions=sorted(
        max((point.X,point.Y,point.Z)[axis] for point in corners)
        -min((point.X,point.Y,point.Z)[axis] for point in corners)
        for axis in range(3)
    )
    return (dimensions[0]+dimensions[1])/2.0


def closest_surface_point(mesh,point):
    mesh_point=mesh.ClosestMeshPoint(point,0.0)
    return mesh_point.Point if mesh_point else None


def embedded_endpoint(source_point,surface_point,overlap):
    direction=surface_point-source_point
    gap=direction.Length
    if not direction.Unitize():
        return surface_point,gap,Rhino.Geometry.Vector3d.Zero
    return surface_point+(direction*overlap),gap,direction


def add_pipe_result(breps,name,index,layer_index):
    ids=[]
    for part_index,brep in enumerate(breps):
        attributes=Rhino.DocObjects.ObjectAttributes()
        attributes.Name=name if len(breps)==1 else name+"_PART_"+str(part_index+1)
        attributes.LayerIndex=layer_index
        attributes.ObjectColor=System.Drawing.Color.FromArgb(210,80,240)
        attributes.ColorSource=Rhino.DocObjects.ObjectColorSource.ColorFromObject
        ids.append(str(sc.doc.Objects.AddBrep(brep,attributes)))
    return ids


def main():
    seat_id=None
    band_id=None
    support_ids=[]
    for object_id in rs.AllObjects(select=False,include_lights=False,include_grips=False) or []:
        name=object_name(object_id)
        upper=name.upper()
        excluded=any(marker in upper for marker in (
            "TRIAL","COPY","REHEARSAL","RESULT","BRIDGE"
        ))
        if "STONE_SEAT" in upper and not excluded:
            seat_id=object_id
        elif "RING_BAND" in upper and not excluded:
            band_id=object_id
        elif "BASKET_SUPPORT" in upper and not excluded and rs.IsObjectSolid(object_id):
            support_ids.append(object_id)

    blockers=[]
    if seat_id is None:
        blockers.append("One original Stone Seat is required.")
    if band_id is None:
        blockers.append("One original Ring Band is required.")
    if len(support_ids)!=2:
        blockers.append("Exactly two original Basket Supports are required.")

    seat_mesh=mesh_for(brep_for(seat_id)) if seat_id else None
    band_mesh=mesh_for(brep_for(band_id)) if band_id else None
    seat_center=centroid(points_of(seat_mesh)) if seat_mesh else None

    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER,color=(210,80,240))
    layer_index=sc.doc.Layers.FindByFullPath(TRIAL_LAYER,-1)

    records=[]
    if not blockers:
        ordered=sorted(support_ids,key=lambda value: object_name(value))
        for index,support_id in enumerate(ordered):
            name=object_name(support_id)
            support_mesh=mesh_for(brep_for(support_id))
            center,bottom_source,top_source=principal_endpoints(points_of(support_mesh))
            bottom_surface=closest_surface_point(band_mesh,bottom_source)
            top_surface=closest_surface_point(seat_mesh,top_source)
            if bottom_surface is None or top_surface is None:
                blockers.append(name+": target surface point unavailable.")
                continue

            bottom,bottom_gap,bottom_direction=embedded_endpoint(
                bottom_source,bottom_surface,CONTACT_OVERLAP_MM
            )
            top,top_gap,top_direction=embedded_endpoint(
                top_source,top_surface,CONTACT_OVERLAP_MM
            )
            outward=Rhino.Geometry.Vector3d(
                center.X-seat_center.X,center.Y-seat_center.Y,0.0
            )
            if not outward.Unitize():
                blockers.append(name+": outward direction unavailable.")
                continue

            diameter=estimated_diameter(support_id)
            bow=diameter*BOW_RATIO
            span=top-bottom
            lower=bottom+(span*0.33)+(outward*(bow*0.55))
            upper=bottom+(span*0.68)+(outward*bow)
            rail=Rhino.Geometry.Curve.CreateInterpolatedCurve(
                [bottom,lower,upper,top],3
            )
            radius=diameter/2.0
            pipes=list(Rhino.Geometry.Brep.CreatePipe(
                rail,radius,False,Rhino.Geometry.PipeCapMode.Flat,
                True,MODEL_TOLERANCE,ANGLE_TOLERANCE
            ) or [])
            trial_name="PTR_CURVED_SUPPORT_TRIAL_{0}".format(index+1)
            result_ids=add_pipe_result(pipes,trial_name,index,layer_index)
            records.append({
                "source_id":str(support_id),
                "source_name":name,
                "trial_name":trial_name,
                "trial_ids":result_ids,
                "diameter_mm":round(diameter,6),
                "radius_mm":round(radius,6),
                "bow_mm":round(bow,6),
                "top_gap_before_mm":round(top_gap,6),
                "bottom_gap_before_mm":round(bottom_gap,6),
                "top_overlap_target_mm":CONTACT_OVERLAP_MM,
                "bottom_overlap_target_mm":CONTACT_OVERLAP_MM,
                "top_contact_target":"STONE_SEAT_100_PERCENT",
                "bottom_contact_target":"RING_BAND_100_PERCENT",
                "pipe_part_count":len(pipes),
            })
    sc.doc.Views.Redraw()

    status=(
        "CURVED_SUPPORT_TRIAL_CREATED"
        if len(support_ids)==2 and len(records)==2 and not blockers
        else "CURVED_SUPPORT_TRIAL_BLOCKED"
    )
    report={
        "generator":"ptr-curved-support-copy-trial-v1",
        "status":status,
        "trial_layer":TRIAL_LAYER,
        "source_support_count":len(support_ids),
        "created_support_count":len(records),
        "records":records,
        "blockers":blockers,
        "original_geometry_modified":False,
        "original_geometry_deleted":False,
        "boolean_executed":False,
        "production_export_allowed":False,
    }
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)

    print("CURVED SUPPORT COPY TRIAL | status="+status)
    print("SUPPORTS | source={0} | created={1}".format(len(support_ids),len(records)))
    for item in records:
        print("CURVED SUPPORT | {0} | diameter_mm={1:.3f} | bow_mm={2:.3f} | top_gap_before_mm={3:.3f} | bottom_gap_before_mm={4:.3f} | top_overlap_target_mm={5:.3f} | bottom_overlap_target_mm={6:.3f}".format(
            item["trial_name"],item["diameter_mm"],item["bow_mm"],
            item["top_gap_before_mm"],item["bottom_gap_before_mm"],
            item["top_overlap_target_mm"],item["bottom_overlap_target_mm"]
        ))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("ORIGINAL GEOMETRY DELETED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("CURVED SUPPORT TRIAL REPORT | "+REPORT_PATH)


if __name__=="__main__":
    main()
'''


def build_curved_support_copy_trial_script(report_path:Path)->str:
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__",json.dumps(str(report_path).replace("\\","/"))
    )


def prepare_curved_support_copy_trial(memory_root:Path,now:datetime|None=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_curved_support_copy_trial.py"
    report_path=memory_root/"Curved_Support_Trials"/f"{stamp}_curved_support_copy_trial.json"
    return script_path,report_path,build_curved_support_copy_trial_script(report_path)


def save_curved_support_copy_trial(script_path:Path,script:str)->None:
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
