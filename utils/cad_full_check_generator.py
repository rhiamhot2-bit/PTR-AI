"""Generate a profile-driven, report-only Rhino full assembly check."""
from datetime import datetime
import json


def full_check_status(profile_valid, counts_valid, topology_valid, dimensions_valid, contacts_valid, tilt_valid):
    if not profile_valid: return "JOB_PROFILE_REQUIRED"
    if not counts_valid: return "FULL_CHECK_BLOCKED_MEMBER_COUNT"
    if not topology_valid: return "FULL_CHECK_BLOCKED_TOPOLOGY"
    if not dimensions_valid: return "FULL_CHECK_BLOCKED_MEMBER_SIZE"
    if not contacts_valid: return "FULL_CHECK_BLOCKED_CONTACT"
    if not tilt_valid: return "FULL_CHECK_BLOCKED_PRONG_TILT"
    return "EDITABLE_ASSEMBLY_READY"


_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Parameterized Full Check
# REPORT ONLY: source parts remain separate and editable.
import io
import json
import math
import os
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

PROFILE = __PROFILE__
REPORT_PATH = __REPORT_PATH__
TOL = float(sc.doc.ModelAbsoluteTolerance)

def name_of(i): return rs.ObjectName(i) or ""
def brep_for(i):
    obj=sc.doc.Objects.Find(i)
    return obj.Geometry if obj and isinstance(obj.Geometry,Rhino.Geometry.Brep) else None
def naked_count(b):
    try: return len(b.DuplicateNakedEdgeCurves(True,True) or [])
    except Exception: return -1
def box(i):
    pts=rs.BoundingBox(i)
    if not pts: return None
    return [min(p.X for p in pts),max(p.X for p in pts),min(p.Y for p in pts),max(p.Y for p in pts),min(p.Z for p in pts),max(p.Z for p in pts)]
def minimum_section(i):
    b=box(i)
    values=[b[1]-b[0],b[3]-b[2],b[5]-b[4]] if b else []
    values=[v for v in values if v>TOL]
    return min(values) if values else 0.0
def contact(a,b):
    try:
        ok,curves,points=Rhino.Geometry.Intersect.Intersection.BrepBrep(brep_for(a),brep_for(b),PROFILE["contact_tolerance_mm"])
        return bool(ok and ((curves and len(curves)) or (points and len(points))))
    except Exception: return False
def axis_tilt(i):
    b=brep_for(i); meshes=Rhino.Geometry.Mesh.CreateFromBrep(b,Rhino.Geometry.MeshingParameters.FastRenderMesh) if b else None
    pts=[Rhino.Geometry.Point3d(v.X,v.Y,v.Z) for m in meshes or [] for v in m.Vertices]
    if len(pts)<4: return None,None
    c=Rhino.Geometry.Point3d(sum(p.X for p in pts)/len(pts),sum(p.Y for p in pts)/len(pts),sum(p.Z for p in pts)/len(pts))
    cov=[[0.0]*3 for _ in range(3)]
    for p in pts:
        q=[p.X-c.X,p.Y-c.Y,p.Z-c.Z]
        for r in range(3):
            for k in range(3): cov[r][k]+=q[r]*q[k]
    v=[0.1,0.1,1.0]
    for _ in range(30):
        n=[sum(cov[r][k]*v[k] for k in range(3)) for r in range(3)]; mag=math.sqrt(sum(x*x for x in n))
        if mag<=0: return None,None
        v=[x/mag for x in n]
    if v[2]<0: v=[-x for x in v]
    radial=[c.X,c.Y]; rmag=math.sqrt(radial[0]**2+radial[1]**2)
    outward=(v[0]*radial[0]+v[1]*radial[1])>0 if rmag>TOL else None
    return math.degrees(math.acos(max(-1,min(1,v[2])))),outward

def main():
    roles={"prongs":[],"supports":[],"seats":[],"bands":[]}
    for i in rs.AllObjects(select=False,include_lights=False,include_grips=False) or []:
        n=name_of(i).upper()
        if "PRONG" in n and not any(x in n for x in ("TRIAL","COPY","REHEARSAL","RESULT")): roles["prongs"].append(i)
        elif "SUPPORT" in n and not any(x in n for x in ("TRIAL","COPY","REHEARSAL","RESULT")): roles["supports"].append(i)
        elif "STONE_SEAT" in n: roles["seats"].append(i)
        elif "RING_BAND" in n: roles["bands"].append(i)
    expected={"prongs":PROFILE["prong_count"],"supports":PROFILE["support_count"],"seats":1,"bands":1}
    counts_valid=all(len(roles[k])==v for k,v in expected.items())
    all_ids=sum(roles.values(),[])
    topology_valid=bool(all_ids and all(rs.IsObjectSolid(i) and naked_count(brep_for(i))==0 for i in all_ids))
    dimensions_valid=all(minimum_section(i)+TOL>=PROFILE["minimum_member_mm"] for i in all_ids)
    seat=roles["seats"][0] if len(roles["seats"])==1 else None
    band=roles["bands"][0] if len(roles["bands"])==1 else None
    contacts=[]
    if seat:
        contacts += [{"a":name_of(i),"b":name_of(seat),"contact":contact(i,seat)} for i in roles["prongs"]]
        contacts += [{"a":name_of(i),"b":name_of(seat),"contact":contact(i,seat)} for i in roles["supports"]]
    if band: contacts += [{"a":name_of(i),"b":name_of(band),"contact":contact(i,band)} for i in roles["supports"]]
    contacts_valid=bool(contacts and all(x["contact"] for x in contacts))
    prong_rows=[]
    for i in roles["prongs"]:
        tilt,outward=axis_tilt(i); target=PROFILE["prong_angle_deg"]
        ready=tilt is not None and abs(tilt-target)<=PROFILE["angle_tolerance_deg"] and (target==0 or outward is True)
        prong_rows.append({"name":name_of(i),"tilt_deg":round(tilt,3) if tilt is not None else None,"outward":outward,"ready":ready})
    tilt_valid=bool(len(prong_rows)==PROFILE["prong_count"] and all(r["ready"] for r in prong_rows))
    status=("FULL_CHECK_BLOCKED_MEMBER_COUNT" if not counts_valid else "FULL_CHECK_BLOCKED_TOPOLOGY" if not topology_valid else "FULL_CHECK_BLOCKED_MEMBER_SIZE" if not dimensions_valid else "FULL_CHECK_BLOCKED_CONTACT" if not contacts_valid else "FULL_CHECK_BLOCKED_PRONG_TILT" if not tilt_valid else "EDITABLE_ASSEMBLY_READY")
    report={"generator":"ptr-parameterized-full-check-v1","status":status,"job_profile":PROFILE,"counts":{k:len(v) for k,v in roles.items()},"prongs":prong_rows,"contacts":contacts,"geometry_modified":False,"document_boolean_executed":False,"production_export_allowed":False,"manual_union_required":status=="EDITABLE_ASSEMBLY_READY"}
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder): os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as h: json.dump(report,h,ensure_ascii=False,indent=2)
    print("PARAMETERIZED CAD FULL CHECK | status="+status)
    print("ASSEMBLY MODE | EDITABLE_NON_UNION")
    print("COUNTS | "+str(report["counts"]))
    for r in prong_rows: print("PRONG | {0} | tilt_deg={1} | outward={2} | ready={3}".format(r["name"],r["tilt_deg"],r["outward"],r["ready"]))
    for r in contacts: print("CONTACT | {0} <-> {1} | ready={2}".format(r["a"],r["b"],r["contact"]))
    print("SOURCE GEOMETRY MODIFIED | NO")
    print("DOCUMENT BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("MANUAL UNION REQUIRED | "+str(status=="EDITABLE_ASSEMBLY_READY"))
    print("FULL CHECK REPORT | "+REPORT_PATH)
if __name__=="__main__": main()
'''


def build_cad_full_check_script(report_path, profile):
    return _TEMPLATE.replace("__PROFILE__", json.dumps(profile, ensure_ascii=False)).replace("__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/")))


def prepare_cad_full_check(memory_root, profile, now=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_parameterized_cad_full_check.py"
    report_path=memory_root/"Parameterized_Full_Checks"/f"{stamp}_parameterized_cad_full_check.json"
    return script_path,report_path,build_cad_full_check_script(report_path,profile)


def save_cad_full_check(path, script):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(script,encoding="utf-8")
