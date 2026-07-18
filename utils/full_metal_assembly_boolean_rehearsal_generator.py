"""Generate a duplicate-only Rhino 8 Full Metal Assembly Boolean Rehearsal."""

from datetime import datetime
import json
from pathlib import Path


def classify_full_assembly(result_count:int,closed:bool,naked_edges:int)->str:
    if result_count==0:
        return "FULL_ASSEMBLY_BOOLEAN_FAILED"
    if result_count!=1:
        return "MULTIPLE_ASSEMBLY_RESULTS"
    if not closed:
        return "ASSEMBLY_NOT_CLOSED"
    if naked_edges:
        return "ASSEMBLY_HAS_NAKED_EDGES"
    return "FULL_METAL_ASSEMBLY_BOOLEAN_REHEARSAL_PASSED"


_SCRIPT_TEMPLATE=r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Full Metal Assembly Boolean Rehearsal
# Uses Duplicate Breps: Band + Seat + 4 trial Prongs + 2 Curved Supports.
import io
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing

REPORT_PATH=__REPORT_PATH__
RESULT_LAYER="PTR_FULL_METAL_ASSEMBLY_BOOLEAN_REHEARSAL"
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


def status_for(count,closed,naked):
    if count==0:
        return "FULL_ASSEMBLY_BOOLEAN_FAILED"
    if count!=1:
        return "MULTIPLE_ASSEMBLY_RESULTS"
    if not closed:
        return "ASSEMBLY_NOT_CLOSED"
    if naked:
        return "ASSEMBLY_HAS_NAKED_EDGES"
    return "FULL_METAL_ASSEMBLY_BOOLEAN_REHEARSAL_PASSED"


def main():
    band_id=None
    seat_id=None
    prong_ids=[]
    support_ids=[]
    for object_id in rs.AllObjects(select=False,include_lights=False,include_grips=False) or []:
        name=object_name(object_id)
        upper=name.upper()
        if upper.endswith("_11DEG_REPOSITION_COPY"):
            prong_ids.append(object_id)
        elif upper.startswith("PTR_CURVED_SUPPORT_TRIAL_"):
            support_ids.append(object_id)
        elif "RING_BAND" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT")
        ):
            band_id=object_id
        elif "STONE_SEAT" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT")
        ):
            seat_id=object_id

    blockers=[]
    if band_id is None:
        blockers.append("One original Ring Band is required.")
    if seat_id is None:
        blockers.append("One original Stone Seat is required.")
    if len(prong_ids)!=4:
        blockers.append("Exactly four validated 11-degree trial Prongs are required.")
    if len(support_ids)!=2:
        blockers.append("Exactly two validated Curved Support trials are required.")

    source_ids=[band_id,seat_id]+prong_ids+support_ids if not blockers else []
    duplicates=[]
    source_records=[]
    for source_id in source_ids:
        brep=brep_for(source_id)
        if brep is None or not brep.IsValid:
            blockers.append(object_name(source_id)+": valid Brep required.")
            continue
        duplicates.append(brep.DuplicateBrep())
        source_records.append({"id":str(source_id),"name":object_name(source_id)})

    results=[]
    if not blockers and len(duplicates)==8:
        try:
            results=list(Rhino.Geometry.Brep.CreateBooleanUnion(
                duplicates,MODEL_TOLERANCE
            ) or [])
        except Exception as error:
            blockers.append("Full assembly Boolean exception: "+str(error))

    if not rs.IsLayer(RESULT_LAYER):
        rs.AddLayer(RESULT_LAYER,color=(30,200,230))
    layer_index=sc.doc.Layers.FindByFullPath(RESULT_LAYER,-1)
    result_ids=[]
    checks=[]
    for index,brep in enumerate(results):
        attributes=Rhino.DocObjects.ObjectAttributes()
        attributes.Name="PTR_FULL_METAL_ASSEMBLY_BOOLEAN_RESULT_{0}".format(index+1)
        attributes.LayerIndex=layer_index
        attributes.ObjectColor=System.Drawing.Color.FromArgb(30,200,230)
        attributes.ColorSource=Rhino.DocObjects.ObjectColorSource.ColorFromObject
        result_id=sc.doc.Objects.AddBrep(brep,attributes)
        result_ids.append(str(result_id))
        checks.append({
            "closed_solid":bool(brep.IsSolid),
            "naked_edge_count":naked_edge_count(brep),
        })
    sc.doc.Views.Redraw()

    count=len(results)
    closed=bool(count==1 and checks[0]["closed_solid"])
    naked=checks[0]["naked_edge_count"] if count==1 else -1
    status=status_for(count,closed,naked)
    if blockers:
        status="FULL_METAL_ASSEMBLY_BOOLEAN_BLOCKED"

    report={
        "generator":"ptr-full-metal-assembly-boolean-rehearsal-v1",
        "status":status,
        "source_counts":{
            "ring_band":1 if band_id else 0,
            "stone_seat":1 if seat_id else 0,
            "trial_prongs":len(prong_ids),
            "curved_supports":len(support_ids),
        },
        "source_records":source_records,
        "duplicate_brep_count":len(duplicates),
        "result_count":count,
        "result_ids":result_ids,
        "result_checks":checks,
        "blockers":blockers,
        "original_geometry_modified":False,
        "original_geometry_deleted":False,
        "boolean_used_original_document_ids":False,
        "production_export_allowed":False,
    }
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)

    print("FULL METAL ASSEMBLY BOOLEAN REHEARSAL | status="+status)
    print("SOURCE COUNTS | band={0} | seat={1} | trial_prongs={2} | curved_supports={3}".format(
        1 if band_id else 0,1 if seat_id else 0,len(prong_ids),len(support_ids)
    ))
    print("DUPLICATE BREPS | count="+str(len(duplicates)))
    print("BOOLEAN RESULTS | count={0} | closed={1} | naked_edges={2}".format(
        count,closed,naked
    ))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("ORIGINAL GEOMETRY DELETED | NO")
    print("BOOLEAN USED ORIGINAL DOCUMENT IDS | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("FULL ASSEMBLY BOOLEAN REPORT | "+REPORT_PATH)


if __name__=="__main__":
    main()
'''


def build_full_metal_assembly_boolean_rehearsal_script(report_path:Path)->str:
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__",json.dumps(str(report_path).replace("\\","/"))
    )


def prepare_full_metal_assembly_boolean_rehearsal(memory_root:Path,now:datetime|None=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_full_metal_assembly_boolean_rehearsal.py"
    report_path=memory_root/"Full_Metal_Assembly_Boolean_Rehearsals"/f"{stamp}_full_metal_assembly_boolean_rehearsal.json"
    return script_path,report_path,build_full_metal_assembly_boolean_rehearsal_script(report_path)


def save_full_metal_assembly_boolean_rehearsal(script_path:Path,script:str)->None:
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
