"""Generate two review-only Rhino shoulder bridge solids."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


GENERATOR_VERSION = "ptr-shoulder-geometry-v1"


def build_shoulder_geometry_script(output_report_json: Path) -> str:
    """Return a Rhino 8 script that creates separate shoulder review geometry."""
    output_text = str(output_report_json).replace("\\", "/")
    template = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Shoulder Geometry Generator
# Generator: ptr-shoulder-geometry-v1
# REVIEW ONLY: creates separate shoulder solids; never Boolean-unions or exports.
import io
import json
import math
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_REPORT = r"__OUTPUT_REPORT__"
GENERATOR = "ptr-shoulder-geometry-v1"
LAYER_NAME = "PTR_SHOULDER_REVIEW"
LEFT_NAME = "PTR_SHOULDER_LEFT"
RIGHT_NAME = "PTR_SHOULDER_RIGHT"
SETTING_MARKERS = ("STONE_SEAT", "PRONG", "BASKET_SUPPORT", "PRODUCTION_METAL")
MIN_OVERLAP_MM = 0.30
SHOULDER_WIDTH_MM = 1.60
SHOULDER_THICKNESS_MM = 1.20


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


def main():
    band = None
    setting_parts = []
    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or "UNNAMED"
        upper = name.upper()
        brep = object_brep(obj_id)
        if not brep:
            continue
        item = {"name": name, "box": brep.GetBoundingBox(True)}
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
        center_x = (setting_box.Min.X + setting_box.Max.X) / 2.0
        center_y = (setting_box.Min.Y + setting_box.Max.Y) / 2.0
        setting_width = setting_box.Max.X - setting_box.Min.X
        offset = max(setting_width * 0.38, SHOULDER_WIDTH_MM)
        start_z = band_box.Max.Z - MIN_OVERLAP_MM
        end_z = setting_box.Min.Z + MIN_OVERLAP_MM
        if end_z <= start_z:
            end_z = start_z + max(MIN_OVERLAP_MM * 2.0, sc.doc.ModelAbsoluteTolerance * 4.0)
            warnings.append("Bounding boxes overlap; a minimum review bridge length was used.")

        previous_layer = rs.CurrentLayer()
        undo_id = sc.doc.BeginUndoRecord("PTR shoulder review geometry")
        try:
            rs.CurrentLayer(ensure_layer())
            for side, object_name, direction in (
                ("LEFT", LEFT_NAME, -1.0),
                ("RIGHT", RIGHT_NAME, 1.0),
            ):
                x = center_x + direction * offset
                start = Rhino.Geometry.Point3d(x, center_y, start_z)
                end = Rhino.Geometry.Point3d(x, center_y, end_z)
                axis = rs.AddLine(start, end)
                shoulder = None
                if axis:
                    shoulder = rs.AddPipe(
                        axis,
                        [0.0, 1.0],
                        [SHOULDER_THICKNESS_MM / 2.0, SHOULDER_THICKNESS_MM / 2.0],
                        blend_type=1,
                        cap=2,
                        fit=True,
                    )
                    rs.DeleteObject(axis)
                if not shoulder:
                    raise RuntimeError("สร้าง shoulder " + side + " ไม่สำเร็จ")
                rs.ObjectName(shoulder, object_name)
                created.append(shoulder)
                bridges.append({
                    "side": side,
                    "name": object_name,
                    "band_anchor": point_data(start),
                    "setting_anchor": point_data(end),
                    "width_mm": SHOULDER_WIDTH_MM,
                    "thickness_mm": SHOULDER_THICKNESS_MM,
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
