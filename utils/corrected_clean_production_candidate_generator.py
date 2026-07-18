"""Generate a clean review-only candidate from the corrected full assembly."""

from datetime import datetime
import json
from pathlib import Path


def corrected_candidate_status(source_count:int, closed:bool, naked_edges:int, volume_mm3:float, stone_collision:bool)->str:
    if source_count!=1:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_SOURCE_COUNT"
    if not closed or naked_edges:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_TOPOLOGY"
    if volume_mm3<=0:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_VOLUME"
    if stone_collision:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_STONE_COLLISION"
    return "CORRECTED_PRODUCTION_CANDIDATE_REVIEW_CREATED"


_SCRIPT_TEMPLATE=r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Corrected Clean Production Candidate
# REVIEW ONLY: copies one corrected assembly result; never exports, deletes, or Booleans.
import io
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing

REPORT_PATH=__REPORT_PATH__
CANDIDATE_LAYER="PTR_CORRECTED_PRODUCTION_CANDIDATE_REVIEW"
MODEL_TOLERANCE=float(sc.doc.ModelAbsoluteTolerance)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj=sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry,Rhino.Geometry.Brep) else None


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
        success,curves,points=Rhino.Geometry.Intersect.Intersection.BrepBrep(first,second,MODEL_TOLERANCE)
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def status_for(count,closed,naked,volume,stone_hit):
    if count!=1:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_SOURCE_COUNT"
    if not closed or naked:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_TOPOLOGY"
    if volume<=0:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_VOLUME"
    if stone_hit:
        return "CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_STONE_COLLISION"
    return "CORRECTED_PRODUCTION_CANDIDATE_REVIEW_CREATED"


def main():
    assembly_ids=[]
    stone_id=None
    for object_id in rs.AllObjects(select=False,include_lights=False,include_grips=False) or []:
        upper=object_name(object_id).upper()
        if upper.startswith("PTR_CORRECTED_FULL_METAL_ASSEMBLY_BOOLEAN_RESULT_"):
            assembly_ids.append(object_id)
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper
            and not any(marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT"))
        ):
            stone_id=object_id

    source_id=assembly_ids[0] if len(assembly_ids)==1 else None
    source_brep=brep_for(source_id) if source_id else None
    closed=bool(source_id and rs.IsObjectSolid(source_id))
    naked=naked_edge_count(source_brep) if source_brep else -1
    volume=volume_of(source_brep) if source_brep else 0.0
    stone_brep=brep_for(stone_id) if stone_id else None
    stone_hit=intersects(source_brep,stone_brep) if source_brep and stone_brep else False
    status=status_for(len(assembly_ids),closed,naked,volume,stone_hit)

    blockers=[]
    if stone_id is None:
        blockers.append("Stone Placeholder is required for collision recheck.")
    if blockers:
        status="CORRECTED_PRODUCTION_CANDIDATE_BLOCKED_PREREQUISITES"

    candidate_id=None
    if status=="CORRECTED_PRODUCTION_CANDIDATE_REVIEW_CREATED":
        if not rs.IsLayer(CANDIDATE_LAYER):
            rs.AddLayer(CANDIDATE_LAYER,color=(245,190,40))
        layer_index=sc.doc.Layers.FindByFullPath(CANDIDATE_LAYER,-1)
        duplicate=source_brep.DuplicateBrep()
        attributes=Rhino.DocObjects.ObjectAttributes()
        attributes.Name="PTR_CORRECTED_PRODUCTION_CANDIDATE_REVIEW_ONLY"
        attributes.LayerIndex=layer_index
        attributes.ObjectColor=System.Drawing.Color.FromArgb(245,190,40)
        attributes.ColorSource=Rhino.DocObjects.ObjectColorSource.ColorFromObject
        attributes.SetUserString("PTR_STATUS","CORRECTED_REVIEW_ONLY")
        attributes.SetUserString("PTR_SOURCE_ASSEMBLY_ID",str(source_id))
        attributes.SetUserString("PTR_READINESS_SCREEN","PASSED")
        attributes.SetUserString("PTR_EXPORT_ALLOWED","NO")
        attributes.SetUserString("PTR_PROFESSIONAL_INSPECTION","REQUIRED")
        attributes.SetUserString("PTR_STONE_INCLUDED","NO")
        candidate_id=sc.doc.Objects.AddBrep(duplicate,attributes)
        sc.doc.Views.Redraw()

    report={
        "generator":"ptr-corrected-clean-production-candidate-v1",
        "status":status,
        "source_assembly_count":len(assembly_ids),
        "source_assembly_id":str(source_id) if source_id else None,
        "candidate_id":str(candidate_id) if candidate_id else None,
        "candidate_layer":CANDIDATE_LAYER,
        "closed_solid":closed,
        "naked_edge_count":naked,
        "volume_mm3":round(volume,6),
        "stone_collision":stone_hit,
        "stone_included":False,
        "blockers":blockers,
        "source_geometry_modified":False,
        "source_geometry_deleted":False,
        "boolean_executed":False,
        "production_export_allowed":False,
        "professional_manufacturing_inspection_required":True,
    }
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)

    print("CORRECTED CLEAN PRODUCTION CANDIDATE | status="+status)
    print("SOURCE ASSEMBLY | count={0} | closed={1} | naked_edges={2} | volume_mm3={3:.3f} | stone_collision={4}".format(len(assembly_ids),closed,naked,volume,stone_hit))
    print("CANDIDATE | id={0} | layer={1} | stone_included=NO".format(str(candidate_id) if candidate_id else "NONE",CANDIDATE_LAYER))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("SOURCE GEOMETRY MODIFIED | NO")
    print("SOURCE GEOMETRY DELETED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED")
    print("CORRECTED PRODUCTION CANDIDATE REPORT | "+REPORT_PATH)


if __name__=="__main__":
    main()
'''


def build_corrected_clean_production_candidate_script(report_path:Path)->str:
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__",json.dumps(str(report_path).replace("\\\\","/")))


def prepare_corrected_clean_production_candidate(memory_root:Path,now:datetime|None=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_corrected_clean_production_candidate.py"
    report_path=memory_root/"Corrected_Production_Candidate_Reviews"/f"{stamp}_corrected_clean_production_candidate.json"
    return script_path,report_path,build_corrected_clean_production_candidate_script(report_path)


def save_corrected_clean_production_candidate(script_path:Path,script:str)->None:
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
