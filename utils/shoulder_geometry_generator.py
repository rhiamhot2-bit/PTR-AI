"""Generate two review-only Rhino shoulder bridge solids."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


GENERATOR_VERSION = "ptr-shoulder-loft-v4"


def build_shoulder_geometry_script(output_report_json: Path) -> str:
    """Return a Rhino 8 script that creates separate shoulder review geometry."""
    output_text = str(output_report_json).replace("\\", "/")
    template = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Shoulder Loft Generator
# Generator: ptr-shoulder-loft-v4
# REVIEW ONLY: creates separate shoulder solids; never Boolean-unions or exports.
import io
import json
import math
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_REPORT = r"__OUTPUT_REPORT__"
GENERATOR = "ptr-shoulder-loft-v4"
LAYER_NAME = "PTR_SHOULDER_REVIEW"
LEFT_NAME = "PTR_SHOULDER_LEFT"
RIGHT_NAME = "PTR_SHOULDER_RIGHT"
SETTING_MARKERS = ("STONE_SEAT", "PRONG", "BASKET_SUPPORT", "PRODUCTION_METAL")
MIN_OVERLAP_MM = 0.35
MIN_CLEARANCE_MM = 0.30
SECTION_STATIONS = (0.0, 0.25, 0.50, 0.75, 1.0)
WIDTH_RADII_MM = (0.82, 0.78, 0.68, 0.58, 0.50)
DEPTH_RADII_MM = (0.52, 0.50, 0.46, 0.42, 0.38)
LOWER_OUTWARD_BOW_MM = 0.32
UPPER_INWARD_EASE_MM = 0.14


def object_brep(obj_id):
    rhino_object = sc.doc.Objects.FindId(obj_id)
    if not rhino_object:
        return None
    return Rhino.Geometry.Brep.TryConvertBrep(rhino_object.Geometry)


def union_box(boxes):
    result = Rhino.Geometry.BoundingBox.Empty
    for box in boxes:
        result.Union(box)
    return result


def ensure_layer():
    if not rs.IsLayer(LAYER_NAME):
        rs.AddLayer(LAYER_NAME, (235, 145, 35))
    return LAYER_NAME


def point_data(point):
    return {"x": round(point.X, 4), "y": round(point.Y, 4), "z": round(point.Z, 4)}


def bbox_gap_mm(first, second):
    dx = max(first.Min.X - second.Max.X, second.Min.X - first.Max.X, 0.0)
    dy = max(first.Min.Y - second.Max.Y, second.Min.Y - first.Max.Y, 0.0)
    dz = max(first.Min.Z - second.Max.Z, second.Min.Z - first.Max.Z, 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def main():
    band = None
    setting_parts = []
    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or "UNNAMED"
        upper = name.upper()
        brep = object_brep(obj_id)
        if not brep:
            continue
        item = {"name": name, "upper": upper, "box": brep.GetBoundingBox(True)}
        if "RING_BAND" in upper and band is None:
            band = item
        elif any(marker in upper for marker in SETTING_MARKERS):
            setting_parts.append(item)

    blockers = []
    warnings = [
        "Review geometry is not production-ready and must be inspected by a jewelry CAD professional.",
        "Verify true surface intersection, minimum wall, comfort, casting flow, and polishing access.",
    ]
    created = []
    bridges = []
    if band is None:
        blockers.append("ไม่พบ RING_BAND ตามมาตรฐานการตั้งชื่อ PTR")
    if not setting_parts:
        blockers.append("ไม่พบชุดกระเปาะตามมาตรฐานการตั้งชื่อ PTR")

    if not blockers:
        band_box = band["box"]
        setting_box = union_box([item["box"] for item in setting_parts])
        seat_parts = [item for item in setting_parts if "STONE_SEAT" in item["upper"]]
        target_box = union_box([item["box"] for item in seat_parts]) if seat_parts else setting_box
        clearance_parts = [
            item for item in setting_parts
            if "PRONG" in item["upper"] or "BASKET_SUPPORT" in item["upper"]
        ]
        center_x = (target_box.Min.X + target_box.Max.X) / 2.0
        center_y = (target_box.Min.Y + target_box.Max.Y) / 2.0
        band_center_x = (band_box.Min.X + band_box.Max.X) / 2.0
        band_center_z = (band_box.Min.Z + band_box.Max.Z) / 2.0
        band_radius_x = (band_box.Max.X - band_box.Min.X) / 2.0
        band_radius_z = (band_box.Max.Z - band_box.Min.Z) / 2.0
        target_half_width = (target_box.Max.X - target_box.Min.X) / 2.0
        if band_radius_x <= 0.0 or band_radius_z <= 0.0 or target_half_width <= MIN_OVERLAP_MM:
            blockers.append("Bounding box ของก้านแหวนหรือฐานกระเปาะไม่สมบูรณ์")

        previous_layer = rs.CurrentLayer()
        undo_id = sc.doc.BeginUndoRecord("PTR shoulder review geometry")
        try:
            rs.CurrentLayer(ensure_layer())
            for side, object_name, direction in (
                ("LEFT", LEFT_NAME, -1.0),
                ("RIGHT", RIGHT_NAME, 1.0),
            ):
                # Place the band anchor wider than v2, then ease inward toward the seat.
                # This produces a flared base and avoids a straight vertical shoulder.
                start_offset = min(max(target_half_width * 0.78, 2.20), band_radius_x * 0.48)
                start_x = band_center_x + direction * start_offset
                normalized_x = min(abs(start_offset / band_radius_x), 0.98)
                band_surface_z = band_center_z + band_radius_z * math.sqrt(max(0.0, 1.0 - normalized_x ** 2))
                start = Rhino.Geometry.Point3d(
                    start_x,
                    center_y,
                    band_surface_z - MIN_OVERLAP_MM,
                )
                end = Rhino.Geometry.Point3d(
                    center_x + direction * max(target_half_width - MIN_OVERLAP_MM, 0.80),
                    center_y,
                    target_box.Min.Z + MIN_OVERLAP_MM,
                )
                rise = end.Z - start.Z
                if rise <= WIDTH_RADII_MM[0] * 1.50:
                    raise RuntimeError("ระยะจากก้านแหวนถึงฐานกระเปาะสั้นเกินไปสำหรับสร้าง shoulder")
                lateral_delta = end.X - start.X
                control_1 = Rhino.Geometry.Point3d(
                    start.X + direction * LOWER_OUTWARD_BOW_MM,
                    center_y,
                    start.Z + rise * 0.20,
                )
                control_2 = Rhino.Geometry.Point3d(
                    start.X + lateral_delta * 0.42 + direction * LOWER_OUTWARD_BOW_MM * 0.45,
                    center_y,
                    start.Z + rise * 0.48,
                )
                control_3 = Rhino.Geometry.Point3d(
                    end.X - lateral_delta * 0.18 - direction * UPPER_INWARD_EASE_MM,
                    center_y,
                    end.Z - rise * 0.20,
                )
                axis = rs.AddInterpCurve(
                    [start, control_1, control_2, control_3, end],
                    degree=3,
                    knotstyle=0,
                )
                shoulder = None
                if axis:
                    axis_curve = rs.coercecurve(axis)
                    parameters = axis_curve.DivideByCount(len(SECTION_STATIONS) - 1, True)
                    section_curves = []
                    if not parameters or len(parameters) != len(SECTION_STATIONS):
                        raise RuntimeError("แบ่งแนวแกน shoulder เป็นหน้าตัดไม่สำเร็จ")
                    for index, parameter in enumerate(parameters):
                        section_point = axis_curve.PointAt(parameter)
                        tangent = axis_curve.TangentAt(parameter)
                        if not tangent.Unitize():
                            raise RuntimeError("หาแนวสัมผัสสำหรับหน้าตัด shoulder ไม่สำเร็จ")
                        depth_axis = Rhino.Geometry.Vector3d.YAxis
                        width_axis = Rhino.Geometry.Vector3d.CrossProduct(tangent, depth_axis)
                        if not width_axis.Unitize():
                            raise RuntimeError("สร้างระนาบหน้าตัด shoulder ไม่สำเร็จ")
                        plane = Rhino.Geometry.Plane(section_point, depth_axis, width_axis)
                        ellipse = Rhino.Geometry.Ellipse(
                            plane,
                            DEPTH_RADII_MM[index],
                            WIDTH_RADII_MM[index],
                        )
                        section_curves.append(ellipse.ToNurbsCurve())
                    lofts = Rhino.Geometry.Brep.CreateFromLoft(
                        section_curves,
                        Rhino.Geometry.Point3d.Unset,
                        Rhino.Geometry.Point3d.Unset,
                        Rhino.Geometry.LoftType.Normal,
                        False,
                    )
                    if not lofts:
                        raise RuntimeError("Loft shoulder " + side + " ไม่สำเร็จ")
                    joined = Rhino.Geometry.Brep.JoinBreps(
                        lofts, sc.doc.ModelAbsoluteTolerance
                    )
                    loft = joined[0] if joined else lofts[0]
                    capped = loft.CapPlanarHoles(sc.doc.ModelAbsoluteTolerance)
                    if capped:
                        loft = capped
                    if not loft.IsSolid:
                        raise RuntimeError("Loft shoulder " + side + " ยังไม่เป็น closed solid")
                    shoulder = sc.doc.Objects.AddBrep(loft)
                    rs.DeleteObject(axis)
                if not shoulder:
                    raise RuntimeError("สร้าง shoulder " + side + " ไม่สำเร็จ")
                rs.ObjectName(shoulder, object_name)
                created.append(shoulder)
                shoulder_brep = object_brep(shoulder)
                shoulder_box = shoulder_brep.GetBoundingBox(True)
                clearance_checks = []
                for item in clearance_parts:
                    gap = bbox_gap_mm(shoulder_box, item["box"])
                    clearance_checks.append({
                        "object": item["name"],
                        "bbox_gap_mm": round(gap, 4),
                        "passes_target": bool(gap >= MIN_CLEARANCE_MM),
                    })
                minimum_clearance = min(
                    [check["bbox_gap_mm"] for check in clearance_checks]
                ) if clearance_checks else None
                if minimum_clearance is not None and minimum_clearance < MIN_CLEARANCE_MM:
                    warnings.append(
                        side + " shoulder has conservative bounding-box clearance below "
                        + str(MIN_CLEARANCE_MM)
                        + " mm; inspect true surfaces in Rhino."
                    )
                bridges.append({
                    "side": side,
                    "name": object_name,
                    "band_anchor": point_data(start),
                    "setting_anchor": point_data(end),
                    "control_points": [
                        point_data(control_1),
                        point_data(control_2),
                        point_data(control_3),
                    ],
                    "construction_method": "elliptical_section_loft",
                    "section_stations": list(SECTION_STATIONS),
                    "section_width_diameters_mm": [
                        round(radius * 2.0, 4) for radius in WIDTH_RADII_MM
                    ],
                    "section_depth_diameters_mm": [
                        round(radius * 2.0, 4) for radius in DEPTH_RADII_MM
                    ],
                    "clearance_method": "bounding_box_conservative",
                    "minimum_clearance_target_mm": MIN_CLEARANCE_MM,
                    "minimum_clearance_bbox_mm": minimum_clearance,
                    "clearance_checks": clearance_checks,
                    "band_anchor_in_bbox": bool(band_box.Contains(start)),
                    "setting_anchor_in_bbox": bool(target_box.Contains(end)),
                    "closed_solid": bool(rs.IsObjectSolid(shoulder)),
                    "requires_manual_review": True,
                })
        except Exception:
            for obj_id in created:
                if rs.IsObject(obj_id):
                    rs.DeleteObject(obj_id)
            raise
        finally:
            rs.CurrentLayer(previous_layer)
            sc.doc.EndUndoRecord(undo_id)

    payload = {
        "generator": GENERATOR,
        "status": "SHOULDER_GEOMETRY_REVIEW_REQUIRED" if created else "SHOULDER_GEOMETRY_BLOCKED",
        "geometry_created": bool(created),
        "created_objects": [bridge["name"] for bridge in bridges],
        "boolean_executed": False,
        "source_geometry_modified": False,
        "production_export_allowed": False,
        "ring_band": band["name"] if band else None,
        "setting_parts": [item["name"] for item in setting_parts],
        "bridges": bridges,
        "blockers": blockers,
        "profile": {
            "construction_method": "elliptical_section_loft",
            "section_count": len(SECTION_STATIONS),
            "base_width_mm": WIDTH_RADII_MM[0] * 2.0,
            "base_depth_mm": DEPTH_RADII_MM[0] * 2.0,
            "top_width_mm": WIDTH_RADII_MM[-1] * 2.0,
            "top_depth_mm": DEPTH_RADII_MM[-1] * 2.0,
            "curve_control_count": 5,
            "minimum_anchor_overlap_mm": MIN_OVERLAP_MM,
            "minimum_clearance_target_mm": MIN_CLEARANCE_MM,
        },
        "warnings": warnings,
    }
    folder = os.path.dirname(OUTPUT_REPORT)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with io.open(OUTPUT_REPORT, "w", encoding="utf-8") as report_file:
        json.dump(payload, report_file, ensure_ascii=False, indent=2)

    print("SHOULDER GEOMETRY | status=" + payload["status"])
    print("CREATED OBJECTS | " + str(len(created)))
    for bridge in bridges:
        print(bridge["side"] + " | " + bridge["name"] + " | closed=" + str(bridge["closed_solid"]))
    print("BOOLEAN | NOT EXECUTED")
    print("SOURCE GEOMETRY MODIFIED | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("SHOULDER BUILD JSON | " + OUTPUT_REPORT)
    sc.doc.Views.Redraw()


if __name__ == "__main__":
    main()
'''
    return template.replace("__OUTPUT_REPORT__", output_text)


def prepare_shoulder_geometry_paths(memory_root: Path) -> tuple[Path, Path]:
    """Return unique script and audit paths."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    report_dir = memory_root / "Shoulder_Builds"
    script_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    return script_dir / f"{stamp}_shoulder_build.py", report_dir / f"{stamp}_shoulder_build.json"


def save_shoulder_geometry_script(path: Path, script: str) -> str:
    path.write_text(script, encoding="utf-8")
    return str(path)
