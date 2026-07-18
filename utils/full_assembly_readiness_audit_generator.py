"""Generate a report-only Full Assembly Manufacturing Readiness Audit."""

from datetime import datetime
import json
from pathlib import Path

MIN_MEMBER_DIAMETER_MM=0.80
MAX_CENTER_OFFSET_MM=0.50


def classify_readiness(
    result_count:int,
    closed:bool,
    naked_edges:int,
    volume_mm3:float,
    minimum_member_mm:float,
    center_offset_mm:float,
    stone_collision:bool,
)->str:
    if result_count!=1:
        return "INVALID_ASSEMBLY_RESULT_COUNT"
    if not closed or naked_edges:
        return "INVALID_ASSEMBLY_TOPOLOGY"
    if volume_mm3<=0:
        return "INVALID_ASSEMBLY_VOLUME"
    if minimum_member_mm<MIN_MEMBER_DIAMETER_MM:
        return "MEMBER_BELOW_MINIMUM"
    if center_offset_mm>MAX_CENTER_OFFSET_MM:
        return "ASSEMBLY_OFF_CENTER"
    if stone_collision:
        return "STONE_COLLISION_REVIEW_REQUIRED"
    return "FULL_ASSEMBLY_READINESS_SCREEN_PASSED"


_SCRIPT_TEMPLATE=r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Full Assembly Manufacturing Readiness Audit
# REPORT ONLY: screening does not alter or export Rhino geometry.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH=__REPORT_PATH__
MIN_MEMBER_DIAMETER_MM=0.80
MAX_CENTER_OFFSET_MM=0.50
MODEL_TOLERANCE=float(sc.doc.ModelAbsoluteTolerance)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj=sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry,Rhino.Geometry.Brep) else None


def bbox_values(object_id):
    corners=list(rs.BoundingBox(object_id) or [])
    mins=[min((point.X,point.Y,point.Z)[axis] for point in corners) for axis in range(3)]
    maxs=[max((point.X,point.Y,point.Z)[axis] for point in corners) for axis in range(3)]
    return mins,maxs


def bbox_dimensions(object_id):
    mins,maxs=bbox_values(object_id)
    return [maxs[axis]-mins[axis] for axis in range(3)]


def bbox_center(object_id):
    mins,maxs=bbox_values(object_id)
    return Rhino.Geometry.Point3d(
        (mins[0]+maxs[0])/2.0,
        (mins[1]+maxs[1])/2.0,
        (mins[2]+maxs[2])/2.0,
    )


def estimated_rod_diameter(object_id):
    values=sorted(bbox_dimensions(object_id))
    return (values[0]+values[1])/2.0


def naked_edge_count(brep):
    try:
        edges=brep.DuplicateNakedEdgeCurves(True,True)
        return len(edges) if edges else 0
    except Exception:
        return -1


def volume_of(brep):
    try:
        properties=Rhino.Geometry.VolumeMassProperties.Compute(brep)
        return properties.Volume if properties else 0.0
    except Exception:
        return 0.0


def intersects(first,second):
    try:
        success,curves,points=Rhino.Geometry.Intersect.Intersection.BrepBrep(
            first,second,MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def status_for(count,closed,naked,volume,minimum_member,offset,stone_hit):
    if count!=1:
        return "INVALID_ASSEMBLY_RESULT_COUNT"
    if not closed or naked:
        return "INVALID_ASSEMBLY_TOPOLOGY"
    if volume<=0:
        return "INVALID_ASSEMBLY_VOLUME"
    if minimum_member<MIN_MEMBER_DIAMETER_MM:
        return "MEMBER_BELOW_MINIMUM"
    if offset>MAX_CENTER_OFFSET_MM:
        return "ASSEMBLY_OFF_CENTER"
    if stone_hit:
        return "STONE_COLLISION_REVIEW_REQUIRED"
    return "FULL_ASSEMBLY_READINESS_SCREEN_PASSED"


def main():
    result_ids=[]
    band_id=None
    stone_id=None
    trial_prong_ids=[]
    original_prong_ids=[]
    original_support_ids=[]
    for object_id in rs.AllObjects(select=False,include_lights=False,include_grips=False) or []:
        name=object_name(object_id)
        upper=name.upper()
        if upper.startswith("PTR_FULL_METAL_ASSEMBLY_BOOLEAN_RESULT_"):
            result_ids.append(object_id)
        elif "RING_BAND" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT")
        ):
            band_id=object_id
        elif upper.endswith("_11DEG_REPOSITION_COPY"):
            trial_prong_ids.append(object_id)
        elif "PRONG" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT")
        ) and rs.IsObjectSolid(object_id):
            original_prong_ids.append(object_id)
        elif "BASKET_SUPPORT" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT","BRIDGE")
        ) and rs.IsObjectSolid(object_id):
            original_support_ids.append(object_id)
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper
            and not any(marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT"))
        ):
            stone_id=object_id

    blockers=[]
    if len(result_ids)!=1:
        blockers.append("Exactly one Full Metal Assembly Boolean result is required.")
    if band_id is None:
        blockers.append("One original Ring Band is required as center reference.")
    if len(trial_prong_ids)!=4:
        blockers.append("Four 11-degree trial Prongs are required.")
    if len(original_prong_ids)!=4:
        blockers.append("Four original Prongs are required as diameter references.")
    if len(original_support_ids)!=2:
        blockers.append("Two original Basket Supports are required as diameter references.")
    if stone_id is None:
        blockers.append("One Stone Placeholder is required for collision screening.")

    result_id=result_ids[0] if len(result_ids)==1 else None
    result_brep=brep_for(result_id) if result_id else None
    closed=bool(result_id and rs.IsObjectSolid(result_id))
    naked=naked_edge_count(result_brep) if result_brep else -1
    volume=volume_of(result_brep) if result_brep else 0.0

    # Use the original Prongs for manufacturing diameter. The tilted trial
    # Prongs have enlarged axis-aligned bounding boxes and overstate diameter.
    prong_diameters=[estimated_rod_diameter(value) for value in original_prong_ids]
    support_diameters=[estimated_rod_diameter(value) for value in original_support_ids]
    band_dimensions=sorted(bbox_dimensions(band_id)) if band_id else []
    band_section=band_dimensions[0] if band_dimensions else 0.0
    member_values=prong_diameters+support_diameters+([band_section] if band_section else [])
    minimum_member=min(member_values) if member_values else 0.0

    center_offset=0.0
    if result_id and band_id:
        result_center=bbox_center(result_id)
        band_center=bbox_center(band_id)
        center_offset=math.sqrt(
            (result_center.X-band_center.X)**2+
            (result_center.Y-band_center.Y)**2
        )

    stone_brep=brep_for(stone_id) if stone_id else None
    stone_hit=intersects(result_brep,stone_brep) if result_brep and stone_brep else False
    status=status_for(
        len(result_ids),closed,naked,volume,minimum_member,center_offset,stone_hit
    )
    if blockers:
        status="FULL_ASSEMBLY_READINESS_AUDIT_BLOCKED"

    report={
        "generator":"ptr-full-assembly-readiness-audit-v1",
        "status":status,
        "assembly_result_count":len(result_ids),
        "assembly_result_id":str(result_id) if result_id else None,
        "closed_solid":closed,
        "naked_edge_count":naked,
        "volume_mm3":round(volume,6),
        "center_offset_xy_mm":round(center_offset,6),
        "maximum_center_offset_mm":MAX_CENTER_OFFSET_MM,
        "prong_reference_diameters_mm":[round(value,6) for value in prong_diameters],
        "prong_diameter_measurement":"ORIGINAL_PRONG_REFERENCE",
        "support_reference_diameters_mm":[round(value,6) for value in support_diameters],
        "band_minimum_section_mm":round(band_section,6),
        "minimum_member_mm":round(minimum_member,6),
        "minimum_member_requirement_mm":MIN_MEMBER_DIAMETER_MM,
        "stone_collision":stone_hit,
        "blockers":blockers,
        "geometry_modified":False,
        "boolean_executed":False,
        "production_export_allowed":False,
        "warning":"Screening audit only; minimum wall thickness, casting, setting, and polishing allowances require professional inspection.",
    }
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)

    print("FULL ASSEMBLY READINESS AUDIT | status="+status)
    print("ASSEMBLY | count={0} | closed={1} | naked_edges={2} | volume_mm3={3:.3f}".format(
        len(result_ids),closed,naked,volume
    ))
    print("MEMBERS | minimum_mm={0:.3f} | required_mm={1:.3f} | center_offset_xy_mm={2:.3f} | stone_collision={3}".format(
        minimum_member,MIN_MEMBER_DIAMETER_MM,center_offset,stone_hit
    ))
    print("PRONG REFERENCE DIAMETERS MM | "+",".join("{0:.3f}".format(value) for value in prong_diameters))
    print("SUPPORT REFERENCE DIAMETERS MM | "+",".join("{0:.3f}".format(value) for value in support_diameters))
    print("BAND MINIMUM SECTION MM | {0:.3f}".format(band_section))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED")
    print("READINESS AUDIT REPORT | "+REPORT_PATH)


if __name__=="__main__":
    main()
'''


def build_full_assembly_readiness_audit_script(report_path:Path)->str:
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__",json.dumps(str(report_path).replace("\\","/"))
    )


def prepare_full_assembly_readiness_audit(memory_root:Path,now:datetime|None=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_full_assembly_readiness_audit.py"
    report_path=memory_root/"Full_Assembly_Readiness_Audits"/f"{stamp}_full_assembly_readiness_audit.json"
    return script_path,report_path,build_full_assembly_readiness_audit_script(report_path)


def save_full_assembly_readiness_audit(script_path:Path,script:str)->None:
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
