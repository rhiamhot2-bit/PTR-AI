"""Generate a report-only Rhino 8 Bridge Contact Validator."""

from datetime import datetime
import json
from pathlib import Path

MIN_OVERLAP_MM = 0.10


def classify_bridge_contact(
    bridge_closed: bool,
    naked_edge_count: int,
    support_intersects: bool,
    band_intersects: bool,
    minimum_overlap_mm: float,
) -> str:
    if not bridge_closed or naked_edge_count:
        return "INVALID_BRIDGE_SOLID"
    if not support_intersects:
        return "NO_SUPPORT_CONTACT"
    if not band_intersects:
        return "NO_BAND_CONTACT"
    if minimum_overlap_mm < MIN_OVERLAP_MM:
        return "OVERLAP_TOO_SHALLOW"
    return "READY_FOR_BOOLEAN_REHEARSAL"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Bridge Contact Validator
# REPORT ONLY: never modifies or exports geometry.
import io
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)
MIN_OVERLAP_MM = 0.10


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


def bbox(object_id):
    corners = rs.BoundingBox(object_id)
    if not corners:
        return None
    values = [(point.X, point.Y, point.Z) for point in corners]
    return (
        [min(point[i] for point in values) for i in range(3)],
        [max(point[i] for point in values) for i in range(3)],
    )


def major_axis(box):
    lengths = [box[1][axis] - box[0][axis] for axis in range(3)]
    return max(range(3), key=lambda axis: lengths[axis])


def overlap_on_axis(first, second, axis):
    return max(0.0, min(first[1][axis], second[1][axis]) - max(first[0][axis], second[0][axis]))


def intersects(first, second):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(
            first, second, MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def naked_edge_count(brep):
    try:
        edges = brep.DuplicateNakedEdgeCurves(True, True)
        return len(edges) if edges else 0
    except Exception:
        return -1


def status_for(closed, naked_count, support_hit, band_hit, minimum_overlap):
    if not closed or naked_count:
        return "INVALID_BRIDGE_SOLID"
    if not support_hit:
        return "NO_SUPPORT_CONTACT"
    if not band_hit:
        return "NO_BAND_CONTACT"
    if minimum_overlap < MIN_OVERLAP_MM:
        return "OVERLAP_TOO_SHALLOW"
    return "READY_FOR_BOOLEAN_REHEARSAL"


def main():
    bridges = []
    supports = []
    bands = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        upper = name.upper()
        brep = brep_for(object_id)
        box = bbox(object_id)
        if brep is None or box is None:
            continue
        item = (object_id, name, brep, box)
        if upper.startswith("PTR_BRIDGE_TRIAL_"):
            bridges.append(item)
        elif "BASKET_SUPPORT" in upper and "BRIDGE_TRIAL" not in upper:
            supports.append(item)
        elif "RING_BAND" in upper and "BRIDGE_TRIAL" not in upper:
            bands.append(item)

    results = []
    for bridge_id, bridge_name, bridge_brep, bridge_box in bridges:
        axis = major_axis(bridge_box)
        support_hits = []
        band_hits = []
        for object_id, name, brep, box in supports:
            if intersects(bridge_brep, brep):
                support_hits.append({
                    "id": str(object_id),
                    "name": name,
                    "overlap_mm": round(overlap_on_axis(bridge_box, box, axis), 6),
                })
        for object_id, name, brep, box in bands:
            if intersects(bridge_brep, brep):
                band_hits.append({
                    "id": str(object_id),
                    "name": name,
                    "overlap_mm": round(overlap_on_axis(bridge_box, box, axis), 6),
                })

        overlaps = [item["overlap_mm"] for item in support_hits + band_hits]
        minimum_overlap = min(overlaps) if overlaps else 0.0
        closed = bool(rs.IsObjectSolid(bridge_id))
        naked_count = naked_edge_count(bridge_brep)
        status = status_for(
            closed,
            naked_count,
            bool(support_hits),
            bool(band_hits),
            minimum_overlap,
        )
        results.append({
            "bridge_id": str(bridge_id),
            "bridge_name": bridge_name,
            "status": status,
            "closed_solid": closed,
            "naked_edge_count": naked_count,
            "major_axis": ("X", "Y", "Z")[axis],
            "support_contacts": support_hits,
            "band_contacts": band_hits,
            "minimum_bbox_overlap_mm": round(minimum_overlap, 6),
        })

    ready_count = sum(item["status"] == "READY_FOR_BOOLEAN_REHEARSAL" for item in results)
    report = {
        "generator": "ptr-bridge-contact-validator-v1",
        "status": "BRIDGE_CONTACT_REVIEW_REQUIRED",
        "bridge_count": len(bridges),
        "ready_count": ready_count,
        "results": results,
        "geometry_modified": False,
        "boolean_executed": False,
        "production_export_allowed": False,
        "warning": "Bounding-box overlap is an estimate; inspect real surfaces before production.",
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("BRIDGE CONTACT VALIDATOR | status=" + report["status"])
    print("BRIDGES | count={0} | ready={1}".format(len(bridges), ready_count))
    for item in results:
        print("BRIDGE CHECK | {0} | {1} | closed={2} | naked_edges={3} | support_contacts={4} | band_contacts={5} | min_overlap_mm={6:.3f}".format(
            item["bridge_name"], item["status"], item["closed_solid"],
            item["naked_edge_count"], len(item["support_contacts"]),
            len(item["band_contacts"]), item["minimum_bbox_overlap_mm"]))
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("BRIDGE CONTACT REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_bridge_contact_validator_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_bridge_contact_validator(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_bridge_contact_validator.py"
    report_path = memory_root / "Bridge_Contact_Reports" / f"{timestamp}_bridge_contact_validator.json"
    return script_path, report_path, build_bridge_contact_validator_script(report_path)


def save_bridge_contact_validator(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
