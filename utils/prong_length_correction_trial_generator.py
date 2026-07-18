"""Generate non-destructive Prong Length Correction trial copies."""

from datetime import datetime
import json
from pathlib import Path


TARGET_ALLOWANCE_MM = 0.80


def required_addition(allowance_mm, target=TARGET_ALLOWANCE_MM):
    return round(max(0.0, target - allowance_mm), 3)


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Prong Length Correction Trial
# TRIAL ONLY: duplicates prongs; never changes originals, Booleans, or exports.
import io
import json
import math
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System.Drawing

REPORT_PATH = __REPORT_PATH__
TRIAL_LAYER = "PTR_PRONG_LENGTH_CORRECTION_TRIAL"
TARGET_ALLOWANCE_MM = 0.80
TARGET_TILT_DEG = 11.0


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def brep_for(object_id):
    obj = sc.doc.Objects.Find(object_id)
    return obj.Geometry if obj and isinstance(obj.Geometry, Rhino.Geometry.Brep) else None


def bounds(object_id):
    box = rs.BoundingBox(object_id)
    if not box:
        return None
    xs = [point.X for point in box]
    ys = [point.Y for point in box]
    zs = [point.Z for point in box]
    return {
        "min_x": min(xs), "max_x": max(xs),
        "min_y": min(ys), "max_y": max(ys),
        "min_z": min(zs), "max_z": max(zs),
        "center": Rhino.Geometry.Point3d(
            (min(xs) + max(xs)) / 2.0,
            (min(ys) + max(ys)) / 2.0,
            (min(zs) + max(zs)) / 2.0,
        ),
    }


def reference_diameter(original_id):
    box = bounds(original_id)
    if not box:
        return 0.0
    values = [
        box["max_x"] - box["min_x"],
        box["max_y"] - box["min_y"],
        box["max_z"] - box["min_z"],
    ]
    positive = [value for value in values if value > 0.000001]
    return min(positive) if positive else 0.0


def volume_of(brep):
    try:
        properties = Rhino.Geometry.VolumeMassProperties.Compute(brep)
        return properties.Volume if properties else 0.0
    except Exception:
        return 0.0


def main():
    source_prongs = []
    originals = {}
    stone_id = None
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        upper = object_name(object_id).upper()
        if upper.startswith("PTR_PRONG_") and "11DEG_REPOSITION_COPY" in upper:
            source_prongs.append(object_id)
        elif upper.startswith("PTR_PRONG_") and all(
            word not in upper for word in ("COPY", "TRIAL", "REHEARSAL", "RESULT", "11DEG")
        ):
            suffix = upper.replace("PTR_PRONG_", "").split("_")[0]
            originals[suffix] = object_id
        elif "STONE_PLACEHOLDER" in upper or (
            "STONE" in upper and "STONE_SEAT" not in upper
            and not any(word in upper for word in ("TRIAL", "COPY", "REHEARSAL", "RESULT"))
        ):
            stone_id = object_id

    stone_box = bounds(stone_id) if stone_id else None
    blockers = []
    if len(source_prongs) != 4:
        blockers.append("Exactly four 11-degree source trial prongs are required.")
    if stone_box is None:
        blockers.append("Stone Placeholder is required.")

    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER, color=(80, 170, 255))
    layer_index = sc.doc.Layers.FindByFullPath(TRIAL_LAYER, -1)

    rows = []
    created = []
    stone_center = stone_box["center"] if stone_box else Rhino.Geometry.Point3d.Origin
    for source_id in sorted(source_prongs, key=object_name):
        name = object_name(source_id)
        box = bounds(source_id)
        brep = brep_for(source_id)
        allowance = box["max_z"] - stone_box["max_z"] if box and stone_box else None
        addition = max(0.0, TARGET_ALLOWANCE_MM - allowance) if allowance is not None else 0.0
        suffix = name.upper().replace("PTR_PRONG_", "").split("_")[0]
        diameter = reference_diameter(originals.get(suffix)) if suffix in originals else 0.0
        volume = volume_of(brep) if brep else 0.0
        length = volume / (math.pi * (diameter / 2.0) ** 2) if diameter > 0 and volume > 0 else 0.0

        created_id = None
        if not blockers and brep and length > 0:
            radial = Rhino.Geometry.Vector3d(
                box["center"].X - stone_center.X,
                box["center"].Y - stone_center.Y,
                0.0,
            )
            if not radial.Unitize():
                blockers.append(name + " radial direction could not be determined.")
            else:
                angle = math.radians(TARGET_TILT_DEG)
                axis = Rhino.Geometry.Vector3d(
                    radial.X * math.sin(angle),
                    radial.Y * math.sin(angle),
                    math.cos(angle),
                )
                axis.Unitize()
                base = box["center"] - axis * (length / 2.0)
                xaxis = Rhino.Geometry.Vector3d.CrossProduct(Rhino.Geometry.Vector3d.ZAxis, axis)
                if not xaxis.Unitize():
                    xaxis = Rhino.Geometry.Vector3d.XAxis
                plane = Rhino.Geometry.Plane(base, xaxis, axis)
                duplicate = brep.DuplicateBrep()
                factor = (length + addition) / length
                duplicate.Transform(Rhino.Geometry.Transform.Scale(plane, 1.0, 1.0, factor))
                attributes = Rhino.DocObjects.ObjectAttributes()
                attributes.Name = name + "_LENGTH_CORRECTION_TRIAL"
                attributes.LayerIndex = layer_index
                attributes.ObjectColor = System.Drawing.Color.FromArgb(80, 170, 255)
                attributes.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
                attributes.SetUserString("PTR_STATUS", "TRIAL_ONLY")
                attributes.SetUserString("PTR_SOURCE_ID", str(source_id))
                attributes.SetUserString("PTR_LENGTH_ADDITION_MM", "{0:.3f}".format(addition))
                attributes.SetUserString("PTR_TARGET_ALLOWANCE_MM", "{0:.3f}".format(TARGET_ALLOWANCE_MM))
                attributes.SetUserString("PTR_PRESERVE_OUTWARD_TILT_DEG", "11.0")
                attributes.SetUserString("PTR_MIN_SEAT_ENGAGEMENT_RATIO", "0.25")
                created_id = sc.doc.Objects.AddBrep(duplicate, attributes)
                if created_id:
                    created.append(created_id)

        rows.append({
            "source": name,
            "source_id": str(source_id),
            "trial_id": str(created_id) if created_id else None,
            "allowance_before_mm": round(allowance, 3) if allowance is not None else None,
            "addition_mm": round(addition, 3),
            "target_allowance_mm": TARGET_ALLOWANCE_MM,
            "reference_diameter_mm": round(diameter, 3),
            "outward_tilt_deg": TARGET_TILT_DEG,
            "base_preserved": True,
        })

    status = (
        "PRONG_LENGTH_CORRECTION_TRIAL_CREATED"
        if len(created) == 4 and not blockers
        else "PRONG_LENGTH_CORRECTION_TRIAL_BLOCKED"
    )
    sc.doc.Views.Redraw()
    report = {
        "generator": "ptr-prong-length-correction-trial-v1",
        "status": status,
        "source_count": len(source_prongs),
        "created_count": len(created),
        "target_allowance_mm": TARGET_ALLOWANCE_MM,
        "prongs": rows,
        "blockers": blockers,
        "source_geometry_modified": False,
        "source_geometry_deleted": False,
        "boolean_executed": False,
        "production_export_allowed": False,
    }
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("PRONG LENGTH CORRECTION TRIAL | status=" + status)
    print("TRIAL PRONGS | source={0} | created={1}".format(len(source_prongs), len(created)))
    for row in rows:
        print("PRONG LENGTH | {0} | before_mm={1} | addition_mm={2:.3f} | target_mm=0.800 | diameter_mm={3:.3f} | outward_tilt_deg=11.0 | base_preserved=True".format(
            row["source"], row["allowance_before_mm"], row["addition_mm"], row["reference_diameter_mm"]
        ))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("TRIAL LAYER | " + TRIAL_LAYER)
    print("SOURCE GEOMETRY MODIFIED | NO")
    print("SOURCE GEOMETRY DELETED | NO")
    print("BOOLEAN | NOT EXECUTED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("PRONG LENGTH TRIAL REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_prong_length_correction_trial_script(report_path):
    return _SCRIPT_TEMPLATE.replace(
        "__REPORT_PATH__", json.dumps(str(report_path).replace("\\", "/"))
    )


def prepare_prong_length_correction_trial(memory_root, now=None):
    stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{stamp}_prong_length_correction_trial.py"
    report_path = memory_root / "Prong_Length_Correction_Trials" / f"{stamp}_prong_length_correction_trial.json"
    return script_path, report_path, build_prong_length_correction_trial_script(report_path)


def save_prong_length_correction_trial(script_path, script):
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
