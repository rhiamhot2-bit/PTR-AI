"""Generate a safe Rhino 8 metal-union rehearsal script."""

from datetime import datetime
import json
from pathlib import Path

GENERATOR_ID = "ptr-metal-union-rehearsal-v1"
REHEARSAL_LAYER = "PTR_METAL_UNION_REHEARSAL"
INCLUDE_MARKERS = (
    "RING_BAND",
    "STONE_SEAT",
    "PRONG",
    "BASKET_SUPPORT",
    "SHOULDER",
    "PRODUCTION_METAL",
)
EXCLUDE_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "GUIDE", "NOTES")


def is_rehearsal_metal_name(name: str) -> bool:
    """Return True only for named production-metal candidates."""
    upper_name = (name or "").upper()
    return (
        any(marker in upper_name for marker in INCLUDE_MARKERS)
        and not any(marker in upper_name for marker in EXCLUDE_MARKERS)
    )


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Metal Union Rehearsal
# Generator: ptr-metal-union-rehearsal-v1
# REHEARSAL ONLY: BooleanUnion runs on copies; original geometry is never passed in.
import io
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
REHEARSAL_LAYER = "PTR_METAL_UNION_REHEARSAL"
INCLUDE_MARKERS = (
    "RING_BAND",
    "STONE_SEAT",
    "PRONG",
    "BASKET_SUPPORT",
    "SHOULDER",
    "PRODUCTION_METAL",
)
EXCLUDE_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "GUIDE", "NOTES")


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def is_rehearsal_metal(object_id):
    name = object_name(object_id).upper()
    return (
        any(marker in name for marker in INCLUDE_MARKERS)
        and not any(marker in name for marker in EXCLUDE_MARKERS)
    )


def naked_edge_count(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return -1
    geometry = rhino_object.Geometry
    if not isinstance(geometry, Rhino.Geometry.Brep):
        return -1
    curves = geometry.DuplicateNakedEdgeCurves(True, True)
    return len(curves) if curves is not None else 0


def ensure_layer():
    if not rs.IsLayer(REHEARSAL_LAYER):
        rs.AddLayer(REHEARSAL_LAYER, color=(255, 140, 0))
    return REHEARSAL_LAYER


def write_report(report):
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as report_file:
        json.dump(report, report_file, ensure_ascii=False, indent=2)


def main():
    source_ids = [
        object_id
        for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False)
        if is_rehearsal_metal(object_id)
    ]
    source_names = [object_name(object_id) for object_id in source_ids]
    ring_bands = [name for name in source_names if "RING_BAND" in name.upper()]
    source_checks = [
        {
            "id": str(object_id),
            "name": object_name(object_id),
            "closed_solid": bool(rs.IsObjectSolid(object_id)),
            "naked_edges": naked_edge_count(object_id),
        }
        for object_id in source_ids
    ]
    blockers = []
    if len(source_ids) < 2:
        blockers.append("At least two eligible metal objects are required.")
    if len(ring_bands) != 1:
        blockers.append("Exactly one ring band is required.")
    for item in source_checks:
        if not item["closed_solid"] or item["naked_edges"] != 0:
            blockers.append("Source is not a clean closed solid: " + item["name"])

    report = {
        "generator": "ptr-metal-union-rehearsal-v1",
        "status": "METAL_UNION_REHEARSAL_BLOCKED" if blockers else "METAL_UNION_REHEARSAL_REVIEW_REQUIRED",
        "source_objects": source_checks,
        "source_count": len(source_ids),
        "copy_ids": [],
        "boolean_result_ids": [],
        "result_closed_solid": False,
        "result_naked_edges": None,
        "original_geometry_modified": False,
        "delete_input": False,
        "production_export_allowed": False,
        "blockers": blockers,
        "error": None,
    }

    copy_ids = []
    result_ids = []
    if not blockers:
        ensure_layer()
        copied = rs.CopyObjects(source_ids)
        copy_ids = list(copied or [])
        report["copy_ids"] = [str(object_id) for object_id in copy_ids]

        for index, object_id in enumerate(copy_ids, 1):
            rs.ObjectLayer(object_id, REHEARSAL_LAYER)
            rs.ObjectName(object_id, "REHEARSAL_COPY__{0:02d}".format(index))

        try:
            # Critical safety rule: Boolean only receives duplicate IDs.
            # delete_input=False keeps the rehearsal copies available for inspection.
            union_result = rs.BooleanUnion(copy_ids, delete_input=False)
            result_ids = list(union_result or [])
            report["boolean_result_ids"] = [str(object_id) for object_id in result_ids]
            for index, object_id in enumerate(result_ids, 1):
                rs.ObjectLayer(object_id, REHEARSAL_LAYER)
                rs.ObjectName(object_id, "PTR_METAL_UNION_REHEARSAL_RESULT_{0}".format(index))

            if len(result_ids) == 1:
                report["result_closed_solid"] = bool(rs.IsObjectSolid(result_ids[0]))
                report["result_naked_edges"] = naked_edge_count(result_ids[0])
                if report["result_closed_solid"] and report["result_naked_edges"] == 0:
                    report["status"] = "METAL_UNION_REHEARSAL_PASSED"
        except Exception as exc:
            report["error"] = str(exc)
            report["status"] = "METAL_UNION_REHEARSAL_REVIEW_REQUIRED"

    print("METAL UNION REHEARSAL | status={0}".format(report["status"]))
    print("SOURCE METAL OBJECTS | count={0}".format(len(source_ids)))
    print("REHEARSAL COPIES | count={0}".format(len(copy_ids)))
    print("BOOLEAN RESULTS | count={0}".format(len(result_ids)))
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    if report["result_naked_edges"] is not None:
        print("RESULT NAKED EDGES | {0}".format(report["result_naked_edges"]))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    if report["error"]:
        print("BOOLEAN ERROR | " + report["error"])
    print("REHEARSAL AUDIT JSON | " + REPORT_PATH)
    print("Professional jewelry-CAD review is required before production.")

    write_report(report)
    rs.Redraw()


if __name__ == "__main__":
    main()
'''


def build_metal_union_rehearsal_script(report_path: Path) -> str:
    """Build the Rhino script with a normalized audit-report path."""
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_metal_union_rehearsal(
    memory_root: Path,
    now: datetime | None = None,
) -> tuple[Path, Path, str]:
    """Return script path, report path, and generated source."""
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_metal_union_rehearsal.py"
    report_path = (
        memory_root
        / "Metal_Union_Rehearsals"
        / f"{timestamp}_metal_union_rehearsal.json"
    )
    return script_path, report_path, build_metal_union_rehearsal_script(report_path)


def save_metal_union_rehearsal(script_path: Path, script: str) -> None:
    """Persist the generated Rhino script."""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
