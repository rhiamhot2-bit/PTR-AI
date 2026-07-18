"""Generate a report-only Corrected Production Finishing Audit."""

from datetime import datetime
import json


def corrected_finishing_status(candidate_count, prong_count, support_count, closed, naked_edges, stone_collision, prongs_ready):
    if candidate_count != 1:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_CANDIDATE"
    if prong_count != 4 or support_count != 2:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_MEMBER_COUNT"
    if not closed or naked_edges:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_TOPOLOGY"
    if stone_collision:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_STONE_COLLISION"
    if not prongs_ready:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_PRONG_FINISH"
    return "CORRECTED_FINISHING_AUDIT_REVIEW_REQUIRED"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Corrected Production Finishing Audit
# REPORT ONLY: never moves, trims, deletes, Booleans, or exports geometry.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
MIN_MEMBER_MM = 0.80
MIN_PRONG_TRIM_MM = 0.80
MAX_PRONG_TRIM_MM = 2.50
TARGET_OUTWARD_TILT_DEG = 11.0
TILT_TOLERANCE_DEG = 0.25
MAX_SYMMETRY_SPREAD_MM = 0.25
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)


def name_of(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj = sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None


def naked_count(brep):
    try:
        curves = brep.DuplicateNakedEdgeCurves(True, True)
        return len(curves) if curves else 0
    except Exception:
        return -1


def bbox(object_id):
    box = rs.BoundingBox(object_id)
    if not box:
        return None
    return {"min_x": min(p.X for p in box), "max_x": max(p.X for p in box),
            "min_y": min(p.Y for p in box), "max_y": max(p.Y for p in box),
            "min_z": min(p.Z for p in box), "max_z": max(p.Z for p in box)}


def min_section(object_id):
    box = bbox(object_id)
    if not box:
        return 0.0
    values = [box["max_x"]-box["min_x"], box["max_y"]-box["min_y"], box["max_z"]-box["min_z"]]
    positive = [v for v in values if v > MODEL_TOLERANCE]
    return min(positive) if positive else 0.0


def center_xy(object_id):
    box = bbox(object_id)
    return ((box["min_x"]+box["max_x"])/2.0, (box["min_y"]+box["max_y"])/2.0) if box else None


def axis_and_tilt(object_id):
    brep = brep_for(object_id)
    meshes = Rhino.Geometry.Mesh.CreateFromBrep(brep, Rhino.Geometry.MeshingParameters.FastRenderMesh) if brep else None
    points = [Rhino.Geometry.Point3d(v.X,v.Y,v.Z) for mesh in meshes or [] for v in mesh.Vertices]
    if len(points) < 4:
        return None, None
    center = Rhino.Geometry.Point3d(sum(p.X for p in points)/len(points),sum(p.Y for p in points)/len(points),sum(p.Z for p in points)/len(points))
    covariance=[[0.0,0.0,0.0] for _ in range(3)]
    for point in points:
        values=[point.X-center.X,point.Y-center.Y,point.Z-center.Z]
        for row in range(3):
            for column in range(3): covariance[row][column]+=values[row]*values[column]
    vector=[0.1,0.1,1.0]
    for _ in range(30):
        nxt=[sum(covariance[row][column]*vector[column] for column in range(3)) for row in range(3)]
        magnitude=math.sqrt(sum(value*value for value in nxt))
        if magnitude <= 0: return None,None
        vector=[value/magnitude for value in nxt]
    axis=Rhino.Geometry.Vector3d(vector[0],vector[1],vector[2])
    if axis.Z < 0: axis.Reverse()
    radial=Rhino.Geometry.Vector3d(center.X,center.Y,0.0)
    if radial.IsTiny(): return None,None
    radial.Unitize()
    tilt=math.degrees(math.acos(max(-1.0,min(1.0,axis.Z))))
    outward=(axis.X*radial.X+axis.Y*radial.Y) > 0.0
    return tilt,outward


def intersects(first, second):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(first, second, MODEL_TOLERANCE)
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def audit_status(candidate_count, prong_count, support_count, closed, naked_edges, stone_collision, prongs_ready):
    if candidate_count != 1:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_CANDIDATE"
    if prong_count != 4 or support_count != 2:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_MEMBER_COUNT"
    if not closed or naked_edges:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_TOPOLOGY"
    if stone_collision:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_STONE_COLLISION"
    if not prongs_ready:
        return "CORRECTED_FINISHING_AUDIT_BLOCKED_PRONG_FINISH"
    return "CORRECTED_FINISHING_AUDIT_REVIEW_REQUIRED"


def main():
    candidates, prongs, supports = [], [], []
    stone_id = None
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        upper = name_of(object_id).upper()
        if upper == "PTR_CORRECTED_PRODUCTION_CANDIDATE_REVIEW_ONLY":
            candidates.append(object_id)
        elif upper.startswith("PTR_PRONG_") and upper.endswith("_LENGTH_CORRECTION_TRIAL"):
            prongs.append(object_id)
        elif upper.startswith("PTR_CURVED_SUPPORT_TRIAL_"):
            supports.append(object_id)
        elif "STONE_PLACEHOLDER" in upper or ("STONE" in upper and "STONE_SEAT" not in upper and not any(w in upper for w in ("TRIAL","COPY","REHEARSAL","RESULT"))):
            stone_id = object_id

    candidate_id = candidates[0] if len(candidates) == 1 else None
    candidate_brep = brep_for(candidate_id) if candidate_id else None
    stone_brep = brep_for(stone_id) if stone_id else None
    closed = bool(candidate_id and rs.IsObjectSolid(candidate_id))
    naked = naked_count(candidate_brep) if candidate_brep else -1
    stone_collision = intersects(candidate_brep, stone_brep) if candidate_brep and stone_brep else False
    stone_box = bbox(stone_id) if stone_id else None

    rows, trim_values = [], []
    for object_id in sorted(prongs, key=name_of):
        box = bbox(object_id)
        trim = box["max_z"] - stone_box["max_z"] if box and stone_box else None
        tilt, outward = axis_and_tilt(object_id)
        diameter = min_section(object_id)
        ready = bool(trim is not None and MIN_PRONG_TRIM_MM <= trim <= MAX_PRONG_TRIM_MM and
                     diameter >= MIN_MEMBER_MM and tilt is not None and
                     abs(tilt-TARGET_OUTWARD_TILT_DEG) <= TILT_TOLERANCE_DEG and outward)
        if trim is not None:
            trim_values.append(trim)
        rows.append({"name": name_of(object_id), "diameter_mm": round(diameter,3),
                     "trim_allowance_mm": round(trim,3) if trim is not None else None,
                     "tilt_deg": round(tilt,3) if tilt is not None else None,
                     "outward": outward, "ready": ready})
    spread = max(trim_values)-min(trim_values) if trim_values else None
    prongs_ready = bool(len(rows)==4 and all(r["ready"] for r in rows) and spread is not None and spread <= MAX_SYMMETRY_SPREAD_MM)
    status = audit_status(len(candidates),len(prongs),len(supports),closed,naked,stone_collision,prongs_ready)
    support_rows = [{"name": name_of(i), "diameter_mm": round(min_section(i),3), "shape":"CURVED",
                     "junction_inspection":"SECTION_OR_CLIPPING_PLANE_REQUIRED"} for i in sorted(supports,key=name_of)]
    blockers=[]
    if stone_id is None: blockers.append("Stone Placeholder is required.")
    if len(candidates)!=1: blockers.append("Exactly one corrected review Candidate is required.")
    if len(prongs)!=4: blockers.append("Exactly four corrected prong trials are required.")
    if len(supports)!=2: blockers.append("Exactly two curved support trials are required.")
    for row in rows:
        if not row["ready"]: blockers.append(row["name"]+" does not satisfy corrected finishing limits.")
    warnings=["Inspect every curved-support junction with Section/ClippingPlane before production.",
              "Confirm stone insertion from the open top before final bench folding."]
    report={"generator":"ptr-corrected-production-finishing-audit-v1","status":status,
            "candidate_count":len(candidates),"candidate_closed":closed,"candidate_naked_edges":naked,
            "stone_collision":stone_collision,"prongs":rows,
            "prong_trim_spread_mm":round(spread,3) if spread is not None else None,
            "supports":support_rows,"blockers":blockers,"warnings":warnings,
            "geometry_modified":False,"temporary_geometry_added":False,"boolean_executed":False,
            "production_export_allowed":False,"professional_inspection_required":True}
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder): os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle: json.dump(report,handle,ensure_ascii=False,indent=2)
    print("CORRECTED PRODUCTION FINISHING AUDIT | status="+status)
    print("CANDIDATE | count={0} | closed={1} | naked_edges={2} | stone_collision={3}".format(len(candidates),closed,naked,stone_collision))
    for row in rows:
        print("CORRECTED PRONG FINISH | {0} | diameter_mm={1} | trim_allowance_mm={2} | tilt_deg={3} | outward={4} | ready={5}".format(row["name"],row["diameter_mm"],row["trim_allowance_mm"],row["tilt_deg"],row["outward"],row["ready"]))
    print("PRONG TRIM SYMMETRY | spread_mm="+str(round(spread,3) if spread is not None else None))
    for row in support_rows: print("CURVED SUPPORT FINISH | {0} | diameter_mm={1} | JUNCTION_REVIEW_REQUIRED".format(row["name"],row["diameter_mm"]))
    for blocker in blockers: print("BLOCKER | "+blocker)
    for warning in warnings: print("WARNING | "+warning)
    print("GEOMETRY MODIFIED | NO")
    print("TEMPORARY GEOMETRY ADDED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PROFESSIONAL MANUFACTURING INSPECTION | REQUIRED")
    print("CORRECTED FINISHING AUDIT REPORT | "+REPORT_PATH)


if __name__ == "__main__": main()
'''


def build_corrected_production_finishing_audit_script(report_path):
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/")))


def prepare_corrected_production_finishing_audit(memory_root, now=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_corrected_production_finishing_audit.py"
    report_path=memory_root/"Corrected_Production_Finishing_Audits"/f"{stamp}_corrected_production_finishing_audit.json"
    return script_path,report_path,build_corrected_production_finishing_audit_script(report_path)


def save_corrected_production_finishing_audit(script_path,script):
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
