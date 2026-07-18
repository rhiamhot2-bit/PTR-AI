"""Generate a report-only Rhino 8 Curved Support Contact Validator."""

from datetime import datetime
import json
from pathlib import Path

MIN_CONTACT_DEPTH_MM=0.15
MAX_DIAMETER_SPREAD_MM=0.05
MAX_LENGTH_SPREAD_MM=0.25


def classify_support(
    closed:bool,
    naked_edges:int,
    seat_depth_mm:float,
    band_depth_mm:float,
)->str:
    if not closed or naked_edges:
        return "INVALID_SUPPORT_SOLID"
    if seat_depth_mm<MIN_CONTACT_DEPTH_MM:
        return "TOP_CONTACT_TOO_SHALLOW"
    if band_depth_mm<MIN_CONTACT_DEPTH_MM:
        return "BOTTOM_CONTACT_TOO_SHALLOW"
    return "READY_FOR_SUPPORT_BOOLEAN_REHEARSAL"


_SCRIPT_TEMPLATE=r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Curved Support Contact Validator
# REPORT ONLY: all intersection Breps remain temporary in memory.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH=__REPORT_PATH__
MIN_CONTACT_DEPTH_MM=0.15
MAX_DIAMETER_SPREAD_MM=0.05
MAX_LENGTH_SPREAD_MM=0.25
MODEL_TOLERANCE=float(sc.doc.ModelAbsoluteTolerance)


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj=sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry,Rhino.Geometry.Brep) else None


def bbox_dimensions(object_id):
    corners=list(rs.BoundingBox(object_id) or [])
    return sorted(
        max((point.X,point.Y,point.Z)[axis] for point in corners)
        -min((point.X,point.Y,point.Z)[axis] for point in corners)
        for axis in range(3)
    )


def estimated_diameter(object_id):
    dimensions=bbox_dimensions(object_id)
    return (dimensions[0]+dimensions[1])/2.0


def volume_of(brep):
    try:
        properties=Rhino.Geometry.VolumeMassProperties.Compute(brep)
        return properties.Volume if properties else 0.0
    except Exception:
        return 0.0


def intersection_pieces(first,second):
    try:
        return list(Rhino.Geometry.Brep.CreateBooleanIntersection(
            first,second,MODEL_TOLERANCE
        ) or [])
    except Exception:
        return []


def equivalent_contact_depth(pieces,radius):
    area=math.pi*radius*radius
    if area<=0:
        return 0.0
    return sum(volume_of(piece) for piece in pieces)/area


def naked_edge_count(brep):
    try:
        edges=brep.DuplicateNakedEdgeCurves(True,True)
        return len(edges) if edges else 0
    except Exception:
        return -1


def status_for(closed,naked,seat_depth,band_depth):
    if not closed or naked:
        return "INVALID_SUPPORT_SOLID"
    if seat_depth<MIN_CONTACT_DEPTH_MM:
        return "TOP_CONTACT_TOO_SHALLOW"
    if band_depth<MIN_CONTACT_DEPTH_MM:
        return "BOTTOM_CONTACT_TOO_SHALLOW"
    return "READY_FOR_SUPPORT_BOOLEAN_REHEARSAL"


def main():
    seat_id=None
    band_id=None
    support_ids=[]
    source_support_ids=[]
    for object_id in rs.AllObjects(select=False,include_lights=False,include_grips=False) or []:
        name=object_name(object_id)
        upper=name.upper()
        if upper.startswith("PTR_CURVED_SUPPORT_TRIAL_"):
            support_ids.append(object_id)
        elif "BASKET_SUPPORT" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT","BRIDGE")
        ) and rs.IsObjectSolid(object_id):
            source_support_ids.append(object_id)
        elif "STONE_SEAT" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT")
        ):
            seat_id=object_id
        elif "RING_BAND" in upper and not any(
            marker in upper for marker in ("TRIAL","COPY","REHEARSAL","RESULT")
        ):
            band_id=object_id

    blockers=[]
    if seat_id is None:
        blockers.append("One original Stone Seat is required.")
    if band_id is None:
        blockers.append("One original Ring Band is required.")
    if len(support_ids)!=2:
        blockers.append("Exactly two Curved Support trials are required.")
    if len(source_support_ids)!=2:
        blockers.append("Exactly two original Basket Supports are required as diameter references.")

    source_diameters=[estimated_diameter(value) for value in source_support_ids]
    reference_diameter=(
        sum(source_diameters)/float(len(source_diameters))
        if source_diameters else 0.0
    )
    seat_brep=brep_for(seat_id) if seat_id else None
    band_brep=brep_for(band_id) if band_id else None
    results=[]
    if not blockers:
        for support_id in sorted(support_ids,key=lambda value:object_name(value)):
            name=object_name(support_id)
            brep=brep_for(support_id)
            # A curved Support's axis-aligned bounding box includes its bow and
            # cannot be used as its tube diameter. Use the two straight original
            # Basket Supports as the manufacturing diameter reference.
            diameter=reference_diameter
            radius=diameter/2.0
            seat_pieces=intersection_pieces(brep,seat_brep)
            band_pieces=intersection_pieces(brep,band_brep)
            seat_depth=equivalent_contact_depth(seat_pieces,radius)
            band_depth=equivalent_contact_depth(band_pieces,radius)
            volume=volume_of(brep)
            area=math.pi*radius*radius
            equivalent_length=volume/area if area else 0.0
            closed=bool(rs.IsObjectSolid(support_id))
            naked=naked_edge_count(brep)
            status=status_for(closed,naked,seat_depth,band_depth)
            results.append({
                "support_id":str(support_id),
                "support_name":name,
                "status":status,
                "closed_solid":closed,
                "naked_edge_count":naked,
                "diameter_mm":round(diameter,6),
                "equivalent_length_mm":round(equivalent_length,6),
                "seat_intersection_solid_count":len(seat_pieces),
                "band_intersection_solid_count":len(band_pieces),
                "top_contact_equivalent_depth_mm":round(seat_depth,6),
                "bottom_contact_equivalent_depth_mm":round(band_depth,6),
            })

    diameters=[item["diameter_mm"] for item in results]
    lengths=[item["equivalent_length_mm"] for item in results]
    diameter_spread=max(diameters)-min(diameters) if diameters else 0.0
    length_spread=max(lengths)-min(lengths) if lengths else 0.0
    symmetry_ok=bool(
        len(results)==2
        and diameter_spread<=MAX_DIAMETER_SPREAD_MM
        and length_spread<=MAX_LENGTH_SPREAD_MM
    )
    ready_count=sum(
        item["status"]=="READY_FOR_SUPPORT_BOOLEAN_REHEARSAL"
        for item in results
    )
    report_status=(
        "CURVED_SUPPORT_CONTACT_READY"
        if ready_count==2 and symmetry_ok and not blockers
        else "CURVED_SUPPORT_CONTACT_REVIEW_REQUIRED"
    )
    report={
        "generator":"ptr-curved-support-contact-validator-v1",
        "status":report_status,
        "support_count":len(support_ids),
        "ready_count":ready_count,
        "minimum_contact_depth_mm":MIN_CONTACT_DEPTH_MM,
        "source_diameter_reference_mm":round(reference_diameter,6),
        "diameter_measurement":"AVERAGE_ORIGINAL_BASKET_SUPPORT_DIAMETER",
        "diameter_spread_mm":round(diameter_spread,6),
        "length_spread_mm":round(length_spread,6),
        "symmetry_ok":symmetry_ok,
        "results":results,
        "blockers":blockers,
        "geometry_modified":False,
        "document_boolean_executed":False,
        "analysis_boolean_intersection_executed":True,
        "production_export_allowed":False,
        "warning":"Equivalent contact depth = temporary intersection volume / Support cross-sectional area.",
    }
    folder=os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH,"w",encoding="utf-8") as handle:
        json.dump(report,handle,ensure_ascii=False,indent=2)

    print("CURVED SUPPORT CONTACT VALIDATOR | status="+report_status)
    print("SUPPORTS | count={0} | ready={1} | diameter_spread_mm={2:.3f} | length_spread_mm={3:.3f}".format(
        len(support_ids),ready_count,diameter_spread,length_spread
    ))
    for item in results:
        print("SUPPORT VALIDATION | {0} | {1} | closed={2} | naked_edges={3} | top_contact_depth_mm={4:.3f} | bottom_contact_depth_mm={5:.3f} | diameter_mm={6:.3f} | equivalent_length_mm={7:.3f}".format(
            item["support_name"],item["status"],item["closed_solid"],
            item["naked_edge_count"],item["top_contact_equivalent_depth_mm"],
            item["bottom_contact_equivalent_depth_mm"],item["diameter_mm"],
            item["equivalent_length_mm"]
        ))
    for blocker in blockers:
        print("BLOCKER | "+blocker)
    print("GEOMETRY MODIFIED | NO")
    print("ANALYSIS BOOLEAN INTERSECTION | IN MEMORY ONLY")
    print("DOCUMENT BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("CURVED SUPPORT CONTACT REPORT | "+REPORT_PATH)


if __name__=="__main__":
    main()
'''


def build_curved_support_contact_validator_script(report_path:Path)->str:
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__",json.dumps(str(report_path).replace("\\","/"))
    )


def prepare_curved_support_contact_validator(memory_root:Path,now:datetime|None=None):
    stamp=(now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path=memory_root/"Rhino_Scripts"/f"{stamp}_curved_support_contact_validator.py"
    report_path=memory_root/"Curved_Support_Contact_Reports"/f"{stamp}_curved_support_contact_validator.json"
    return script_path,report_path,build_curved_support_contact_validator_script(report_path)


def save_curved_support_contact_validator(script_path:Path,script:str)->None:
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text(script,encoding="utf-8")
