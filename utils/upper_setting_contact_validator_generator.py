"""Generate a report-only Rhino 8 Upper Setting Contact Validator."""

from datetime import datetime
import json
from pathlib import Path

MIN_OVERLAP_DEPTH_MM = 0.10


def classify_upper_contact(
    valid_solids: bool,
    surface_intersection: bool,
    overlap_volume_mm3: float,
    overlap_depth_mm: float,
) -> str:
    if not valid_solids:
        return "INVALID_METAL_SOLID"
    if not surface_intersection and overlap_volume_mm3 <= 0:
        return "NO_SURFACE_INTERSECTION"
    if overlap_volume_mm3 <= 0:
        return "CONTACT_ONLY_NO_VOLUME_OVERLAP"
    if overlap_depth_mm < MIN_OVERLAP_DEPTH_MM:
        return "OVERLAP_TOO_SHALLOW"
    return "READY_FOR_UPPER_BOOLEAN_REHEARSAL"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Upper Setting Contact Validator
# REPORT ONLY: all intersection geometry remains in memory.
import io
import itertools
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
MODEL_TOLERANCE = float(sc.doc.ModelAbsoluteTolerance)
MIN_OVERLAP_DEPTH_MM = 0.10


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return None
    geometry = rhino_object.Geometry
    return geometry if isinstance(geometry, Rhino.Geometry.Brep) else None


def is_original(name):
    value = name.upper()
    return not any(marker in value for marker in (
        "REHEARSAL", "TRIAL", "COPY", "RESULT", "STONE_PLACEHOLDER", "GIRDLE_GUIDE"
    ))


def role(name):
    value = name.upper()
    if not is_original(name):
        return None
    if "STONE_SEAT" in value:
        return "SEAT"
    if "PRONG" in value:
        return "PRONG"
    if "BASKET_SUPPORT" in value:
        return "SUPPORT"
    return None


def surface_intersection(first, second):
    try:
        success, curves, points = Rhino.Geometry.Intersect.Intersection.BrepBrep(
            first, second, MODEL_TOLERANCE
        )
        return bool(success and ((curves and len(curves)) or (points and len(points))))
    except Exception:
        return False


def boolean_overlap(first, second):
    try:
        pieces = Rhino.Geometry.Brep.CreateBooleanIntersection(
            [first], [second], MODEL_TOLERANCE
        )
    except Exception:
        pieces = None
    if not pieces:
        return 0.0, 0.0, 0
    total_volume = 0.0
    depths = []
    for piece in pieces:
        properties = Rhino.Geometry.VolumeMassProperties.Compute(piece)
        if properties:
            total_volume += abs(properties.Volume)
        box = piece.GetBoundingBox(True)
        dimensions = (
            box.Max.X - box.Min.X,
            box.Max.Y - box.Min.Y,
            box.Max.Z - box.Min.Z,
        )
        positive = [value for value in dimensions if value > MODEL_TOLERANCE]
        if positive:
            depths.append(min(positive))
    return total_volume, (min(depths) if depths else 0.0), len(pieces)


def contact_status(valid, intersects, volume, depth):
    if not valid:
        return "INVALID_METAL_SOLID"
    if not intersects and volume <= 0:
        return "NO_SURFACE_INTERSECTION"
    if volume <= 0:
        return "CONTACT_ONLY_NO_VOLUME_OVERLAP"
    if depth < MIN_OVERLAP_DEPTH_MM:
        return "OVERLAP_TOO_SHALLOW"
    return "READY_FOR_UPPER_BOOLEAN_REHEARSAL"


def main():
    seats = []
    prongs = []
    supports = []
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        item_role = role(name)
        if item_role is None:
            continue
        item = {
            "id": object_id,
            "name": name,
            "brep": brep_for(object_id),
            "closed": bool(rs.IsObjectSolid(object_id)),
        }
        if item_role == "SEAT":
            seats.append(item)
        elif item_role == "PRONG":
            prongs.append(item)
        elif item_role == "SUPPORT":
            supports.append(item)

    blockers = []
    if len(seats) != 1:
        blockers.append("Exactly one original Stone Seat is required.")
    if len(prongs) != 4:
        blockers.append("Exactly four original Prongs are required.")
    if len(supports) != 2:
        blockers.append("Exactly two original Basket Supports are required.")

    results = []
    if not blockers:
        seat = seats[0]
        for target in prongs + supports:
            valid = (
                seat["brep"] is not None and target["brep"] is not None
                and seat["closed"] and target["closed"]
            )
            intersects = surface_intersection(seat["brep"], target["brep"]) if valid else False
            volume, depth, piece_count = (
                boolean_overlap(seat["brep"], target["brep"]) if valid else (0.0, 0.0, 0)
            )
            status = contact_status(valid, intersects, volume, depth)
            results.append({
                "seat_id": str(seat["id"]),
                "seat_name": seat["name"],
                "target_id": str(target["id"]),
                "target_name": target["name"],
                "target_role": "PRONG" if target in prongs else "SUPPORT",
                "status": status,
                "closed_solids": valid,
                "surface_intersection": intersects,
                "overlap_piece_count": piece_count,
                "overlap_volume_mm3": round(volume, 6),
                "minimum_overlap_depth_mm": round(depth, 6),
            })

    ready_count = sum(
        item["status"] == "READY_FOR_UPPER_BOOLEAN_REHEARSAL" for item in results
    )
    report = {
        "generator": "ptr-upper-setting-contact-validator-v1",
        "status": "UPPER_SETTING_CONTACT_REVIEW_REQUIRED" if not blockers else "UPPER_SETTING_CONTACT_BLOCKED",
        "expected_pair_count": 6,
        "pair_count": len(results),
        "ready_count": ready_count,
        "minimum_overlap_depth_mm": MIN_OVERLAP_DEPTH_MM,
        "results": results,
        "blockers": blockers,
        "geometry_modified": False,
        "boolean_geometry_added_to_document": False,
        "production_export_allowed": False,
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("UPPER SETTING CONTACT VALIDATOR | status=" + report["status"])
    print("UPPER PAIRS | count={0} | ready={1}".format(len(results), ready_count))
    for item in results:
        print("UPPER CHECK | {0} <-> {1} | {2} | surface_intersection={3} | overlap_volume_mm3={4:.4f} | min_overlap_depth_mm={5:.3f}".format(
            item["seat_name"], item["target_name"], item["status"],
            item["surface_intersection"], item["overlap_volume_mm3"],
            item["minimum_overlap_depth_mm"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("GEOMETRY MODIFIED | NO")
    print("BOOLEAN GEOMETRY ADDED TO DOCUMENT | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("UPPER CONTACT REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_upper_setting_contact_validator_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_upper_setting_contact_validator(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_upper_setting_contact_validator.py"
    report_path = memory_root / "Upper_Setting_Contact_Reports" / f"{timestamp}_upper_setting_contact_validator.json"
    return script_path, report_path, build_upper_setting_contact_validator_script(report_path)


def save_upper_setting_contact_validator(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
