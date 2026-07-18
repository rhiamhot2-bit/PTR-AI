"""Generate a copy-only Rhino 8 Bridge Boolean Rehearsal."""

from datetime import datetime
import json
from pathlib import Path


def rehearsal_status(result_count: int, closed: bool, naked_edges: int) -> str:
    if result_count != 1:
        return "BOOLEAN_RESULT_COUNT_INVALID"
    if not closed:
        return "BOOLEAN_RESULT_NOT_CLOSED"
    if naked_edges:
        return "BOOLEAN_RESULT_HAS_NAKED_EDGES"
    return "BRIDGE_BOOLEAN_REHEARSAL_PASSED"


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Bridge Boolean Rehearsal
# COPY ONLY: original object IDs are never Booleaned or deleted.
import io
import json
import os

import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

REPORT_PATH = __REPORT_PATH__
TRIAL_LAYER = "PTR_BRIDGE_BOOLEAN_REHEARSAL"


def object_name(object_id):
    return rs.ObjectName(object_id) or ""


def source_role(name):
    value = name.upper()
    if "REHEARSAL_COPY" in value or "BOOLEAN_REHEARSAL_RESULT" in value:
        return None
    if value.startswith("PTR_BRIDGE_TRIAL_"):
        return "BRIDGE"
    if "BASKET_SUPPORT" in value and "BRIDGE_TRIAL" not in value:
        return "SUPPORT"
    if "RING_BAND" in value and "BRIDGE_TRIAL" not in value:
        return "BAND"
    return None


def naked_edge_count(object_id):
    rhino_object = sc.doc.Objects.Find(object_id)
    if rhino_object is None:
        return -1
    geometry = rhino_object.Geometry
    if not isinstance(geometry, Rhino.Geometry.Brep):
        return -1
    edges = geometry.DuplicateNakedEdgeCurves(True, True)
    return len(edges) if edges else 0


def main():
    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER)

    sources = []
    role_counts = {"BAND": 0, "SUPPORT": 0, "BRIDGE": 0}
    for object_id in rs.AllObjects(select=False, include_lights=False, include_grips=False) or []:
        name = object_name(object_id)
        role = source_role(name)
        if role is None or not rs.IsObjectSolid(object_id):
            continue
        sources.append((object_id, name, role))
        role_counts[role] += 1

    blockers = []
    if role_counts["BAND"] != 1:
        blockers.append("Exactly one Ring Band is required.")
    if role_counts["SUPPORT"] != 2:
        blockers.append("Exactly two Basket Supports are required.")
    if role_counts["BRIDGE"] != 2:
        blockers.append("Exactly two validated Bridge Trial solids are required.")

    source_ids = [str(item[0]) for item in sources]
    copy_ids = []
    copy_records = []
    result_ids = []

    if not blockers:
        for source_id, source_name, role in sources:
            copy_id = rs.CopyObject(source_id)
            if not copy_id:
                blockers.append("Copy failed: " + source_name)
                break
            copy_name = source_name + "_REHEARSAL_COPY"
            rs.ObjectName(copy_id, copy_name)
            rs.ObjectLayer(copy_id, TRIAL_LAYER)
            rs.ObjectColor(copy_id, (80, 170, 255))
            copy_ids.append(copy_id)
            copy_records.append({
                "source_id": str(source_id),
                "copy_id": str(copy_id),
                "copy_name": copy_name,
                "role": role,
            })

    if not blockers and len(copy_ids) == 5:
        union_result = rs.BooleanUnion(copy_ids, delete_input=False)
        result_ids = list(union_result or [])
        for index, result_id in enumerate(result_ids, 1):
            rs.ObjectName(result_id, "PTR_BRIDGE_BOOLEAN_REHEARSAL_RESULT_{0}".format(index))
            rs.ObjectLayer(result_id, TRIAL_LAYER)
            rs.ObjectColor(result_id, (0, 220, 120))

    result_count = len(result_ids)
    result_closed = result_count == 1 and bool(rs.IsObjectSolid(result_ids[0]))
    result_naked_edges = naked_edge_count(result_ids[0]) if result_count == 1 else -1

    if blockers:
        status = "BRIDGE_BOOLEAN_REHEARSAL_BLOCKED"
    elif result_count != 1:
        status = "BOOLEAN_RESULT_COUNT_INVALID"
    elif not result_closed:
        status = "BOOLEAN_RESULT_NOT_CLOSED"
    elif result_naked_edges:
        status = "BOOLEAN_RESULT_HAS_NAKED_EDGES"
    else:
        status = "BRIDGE_BOOLEAN_REHEARSAL_PASSED"

    report = {
        "generator": "ptr-bridge-boolean-rehearsal-v1",
        "status": status,
        "role_counts": role_counts,
        "source_ids": source_ids,
        "copies": copy_records,
        "result_ids": [str(item) for item in result_ids],
        "result_count": result_count,
        "result_closed_solid": result_closed,
        "result_naked_edge_count": result_naked_edges,
        "blockers": blockers,
        "original_geometry_modified": False,
        "original_geometry_deleted": False,
        "boolean_used_original_ids": False,
        "delete_input": False,
        "production_export_allowed": False,
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("BRIDGE BOOLEAN REHEARSAL | status=" + status)
    print("SOURCE COUNTS | band={0} | supports={1} | bridges={2}".format(
        role_counts["BAND"], role_counts["SUPPORT"], role_counts["BRIDGE"]))
    print("COPIES | count={0}".format(len(copy_ids)))
    print("BOOLEAN RESULTS | count={0} | closed={1} | naked_edges={2}".format(
        result_count, result_closed, result_naked_edges))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("ORIGINAL GEOMETRY DELETED | NO")
    print("BOOLEAN USED ORIGINAL IDS | NO")
    print("DELETE INPUT | FALSE")
    print("PRODUCTION EXPORT | BLOCKED")
    print("REHEARSAL REPORT | " + REPORT_PATH)


if __name__ == "__main__":
    main()
'''


def build_bridge_boolean_rehearsal_script(report_path: Path) -> str:
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_bridge_boolean_rehearsal(memory_root: Path, now: datetime | None = None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_path = memory_root / "Rhino_Scripts" / f"{timestamp}_bridge_boolean_rehearsal.py"
    report_path = memory_root / "Bridge_Boolean_Rehearsals" / f"{timestamp}_bridge_boolean_rehearsal.json"
    return script_path, report_path, build_bridge_boolean_rehearsal_script(report_path)


def save_bridge_boolean_rehearsal(script_path: Path, script: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
