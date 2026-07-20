"""Generate a Rhino 8 copy-only stone-seat thickness correction trial."""

from datetime import datetime
from pathlib import Path
import json


SOURCE_NAME = "PTR_OVAL_STONE_SEAT_CONCEPT"
TRIAL_NAME = "PTR_OVAL_STONE_SEAT_THICKNESS_CORRECTION_TRIAL"
TRIAL_LAYER = "PTR_SEAT_THICKNESS_CORRECTION_TRIAL"
DEFAULT_MINIMUM_MEMBER_MM = 0.8


def _target_from_profile(memory_root):
    profile_path = Path(memory_root) / "Job_Profiles" / "current.json"
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        return float(profile.get("minimum_member_mm", DEFAULT_MINIMUM_MEMBER_MM))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return DEFAULT_MINIMUM_MEMBER_MM


def prepare_seat_thickness_correction_trial(memory_root):
    memory_root = Path(memory_root)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_seat_thickness_correction_trial.py"
    report_path = memory_root / "Seat_Thickness_Correction_Trials" / f"{stamp}_seat_thickness_correction_trial.json"
    target = _target_from_profile(memory_root)
    script = _render_script(report_path.as_posix(), target)
    return script_path, report_path, script


def save_seat_thickness_correction_trial(script_path, script):
    script_path = Path(script_path)
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")


def _render_script(report_path, target_mm):
    return f'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Seat Thickness Correction Trial
# COPY ONLY: never changes, deletes, joins, Booleans, or exports source geometry.
import io
import json
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

SOURCE_NAME = {SOURCE_NAME!r}
TRIAL_NAME = {TRIAL_NAME!r}
TRIAL_LAYER = {TRIAL_LAYER!r}
TARGET_MM = {target_mm!r}
REPORT_PATH = {report_path!r}


def write_report(payload):
    folder = __import__("os").path.dirname(REPORT_PATH)
    if folder and not __import__("os").path.isdir(folder):
        __import__("os").makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)


def main():
    matches = [object_id for object_id in rs.AllObjects() if (rs.ObjectName(object_id) or "") == SOURCE_NAME]
    if len(matches) != 1:
        status = "SOURCE_NOT_UNIQUE"
        print("SEAT THICKNESS CORRECTION TRIAL | status=" + status)
        print("SOURCE COUNT | count=" + str(len(matches)))
        write_report({{"status": status, "source_count": len(matches), "geometry_modified": False}})
        return

    source_id = matches[0]
    source = sc.doc.Objects.Find(source_id)
    if source is None or not isinstance(source.Geometry, Rhino.Geometry.Brep):
        status = "SOURCE_NOT_BREP"
        print("SEAT THICKNESS CORRECTION TRIAL | status=" + status)
        write_report({{"status": status, "geometry_modified": False}})
        return

    geometry = source.Geometry.DuplicateBrep()
    bbox = geometry.GetBoundingBox(True)
    extents = [bbox.Max.X-bbox.Min.X, bbox.Max.Y-bbox.Min.Y, bbox.Max.Z-bbox.Min.Z]
    axis_index = extents.index(min(extents))
    before_mm = extents[axis_index]
    scale = 1.0 if before_mm >= TARGET_MM else TARGET_MM / before_mm
    factors = [1.0, 1.0, 1.0]
    factors[axis_index] = scale
    center = bbox.Center
    transform = Rhino.Geometry.Transform.Scale(Rhino.Geometry.Plane(center, Rhino.Geometry.Vector3d.XAxis, Rhino.Geometry.Vector3d.YAxis), factors[0], factors[1], factors[2])
    geometry.Transform(transform)

    layer = sc.doc.Layers.FindName(TRIAL_LAYER)
    layer_index = layer.Index if layer else sc.doc.Layers.Add(TRIAL_LAYER, __import__("System").Drawing.Color.DeepSkyBlue)
    attributes = Rhino.DocObjects.ObjectAttributes()
    attributes.Name = TRIAL_NAME
    attributes.LayerIndex = layer_index
    trial_id = sc.doc.Objects.AddBrep(geometry, attributes)
    sc.doc.Views.Redraw()

    after_bbox = geometry.GetBoundingBox(True)
    after_extents = [after_bbox.Max.X-after_bbox.Min.X, after_bbox.Max.Y-after_bbox.Min.Y, after_bbox.Max.Z-after_bbox.Min.Z]
    after_mm = min(after_extents)
    status = "SEAT_THICKNESS_CORRECTION_TRIAL_CREATED"
    print("SEAT THICKNESS CORRECTION TRIAL | status=" + status)
    print("SEAT TRIAL | source=" + SOURCE_NAME + " | trial=" + TRIAL_NAME + " | axis=" + "XYZ"[axis_index] + " | before_mm=" + format(before_mm, ".3f") + " | target_mm=" + format(TARGET_MM, ".3f") + " | after_mm=" + format(after_mm, ".3f"))
    print("SOURCE GEOMETRY MODIFIED | NO")
    print("SOURCE GEOMETRY DELETED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    write_report({{"status": status, "source": SOURCE_NAME, "trial": TRIAL_NAME, "trial_id": str(trial_id), "axis": "XYZ"[axis_index], "before_mm": before_mm, "target_mm": TARGET_MM, "after_mm": after_mm, "source_geometry_modified": False, "source_geometry_deleted": False, "boolean_executed": False, "production_export": "BLOCKED"}})


if __name__ == "__main__":
    main()
'''
