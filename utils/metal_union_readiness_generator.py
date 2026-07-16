"""Generate a report-only Rhino 8 metal-union readiness audit."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

CONTACT_TOLERANCE_MM = 0.05
INCLUDE_MARKERS = (
    "RING_BAND",
    "STONE_SEAT",
    "PRONG",
    "BASKET_SUPPORT",
    "SHOULDER",
    "PRODUCTION_METAL",
)
EXCLUDE_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "GUIDE", "NOTES")


def is_metal_name(name: str | None) -> bool:
    """Return True only for named production-metal candidates."""
    upper = (name or "").upper()
    return (
        any(marker in upper for marker in INCLUDE_MARKERS)
        and not any(marker in upper for marker in EXCLUDE_MARKERS)
    )


def bbox_gap(
    box_a: Sequence[float], box_b: Sequence[float]
) -> float:
    """Return the Euclidean separation between two axis-aligned bounding boxes."""
    if len(box_a) != 6 or len(box_b) != 6:
        raise ValueError("bounding boxes must contain six numbers")

    gaps = []
    for low_a, high_a, low_b, high_b in (
        (box_a[0], box_a[3], box_b[0], box_b[3]),
        (box_a[1], box_a[4], box_b[1], box_b[4]),
        (box_a[2], box_a[5], box_b[2], box_b[5]),
    ):
        gaps.append(max(0.0, low_b - high_a, low_a - high_b))
    return sum(value * value for value in gaps) ** 0.5


def connected_components(
    names: Iterable[str], edges: Iterable[tuple[str, str]]
) -> list[list[str]]:
    """Return deterministic connected components for the supplied contact graph."""
    ordered = list(dict.fromkeys(names))
    adjacency = {name: set() for name in ordered}
    for left, right in edges:
        if left in adjacency and right in adjacency:
            adjacency[left].add(right)
            adjacency[right].add(left)

    components: list[list[str]] = []
    unseen = set(ordered)
    for start in ordered:
        if start not in unseen:
            continue
        stack = [start]
        unseen.remove(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in sorted(adjacency[current], reverse=True):
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    return components


_SCRIPT_TEMPLATE = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Metal Union Readiness Validator
# Generator: ptr-metal-union-readiness-v1
# REPORT ONLY: never creates, joins, deletes, moves, renames, or exports geometry.
import io
import json
import math
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

REPORT_PATH = __REPORT_PATH__
CONTACT_TOLERANCE_MM = 0.05
INCLUDE_MARKERS = (
    "RING_BAND", "STONE_SEAT", "PRONG", "BASKET_SUPPORT",
    "SHOULDER", "PRODUCTION_METAL"
)
EXCLUDE_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "GUIDE", "NOTES")


def is_metal_name(name):
    upper = (name or "").upper()
    included = any(marker in upper for marker in INCLUDE_MARKERS)
    excluded = any(marker in upper for marker in EXCLUDE_MARKERS)
    return included and not excluded


def bbox_values(object_id):
    points = rs.BoundingBox(object_id)
    if not points:
        return None
    xs = [point.X for point in points]
    ys = [point.Y for point in points]
    zs = [point.Z for point in points]
    return [min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)]


def bbox_gap(box_a, box_b):
    gaps = []
    axes = ((0, 3), (1, 4), (2, 5))
    for low_index, high_index in axes:
        gaps.append(max(
            0.0,
            box_b[low_index] - box_a[high_index],
            box_a[low_index] - box_b[high_index],
        ))
    return math.sqrt(sum(value * value for value in gaps))


def graph_components(labels, edges):
    adjacency = dict((label, set()) for label in labels)
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    components = []
    unseen = set(labels)
    for start in labels:
        if start not in unseen:
            continue
        stack = [start]
        unseen.remove(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbour in sorted(adjacency[current], reverse=True):
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    return components


def audit_object(object_id):
    name = rs.ObjectName(object_id) or str(object_id)
    obj_ref = Rhino.DocObjects.ObjRef(object_id)
    brep = obj_ref.Brep()
    closed = bool(brep and brep.IsSolid)
    naked_edges = []
    if brep:
        naked_edges = brep.DuplicateNakedEdgeCurves(True, True) or []
    return {
        "id": str(object_id),
        "name": name,
        "label": name + "|" + str(object_id),
        "closed_solid": closed,
        "naked_edges": len(naked_edges),
        "bbox": bbox_values(object_id),
        "passed": closed and len(naked_edges) == 0,
    }


def main():
    object_ids = rs.AllObjects(select=False, include_lights=False, include_grips=False) or []
    metal_ids = [
        object_id for object_id in object_ids
        if is_metal_name(rs.ObjectName(object_id))
    ]
    records = [audit_object(object_id) for object_id in metal_ids]
    edges = []
    contacts = []
    for index, left in enumerate(records):
        for right in records[index + 1:]:
            if left["bbox"] is None or right["bbox"] is None:
                continue
            gap = bbox_gap(left["bbox"], right["bbox"])
            if gap <= CONTACT_TOLERANCE_MM:
                edges.append((left["label"], right["label"]))
                contacts.append({
                    "left": left["name"],
                    "right": right["name"],
                    "bbox_gap_mm": round(gap, 6),
                })

    labels = [record["label"] for record in records]
    components = graph_components(labels, edges)
    ring_bands = [
        record for record in records if "RING_BAND" in record["name"].upper()
    ]
    invalid = [record["name"] for record in records if not record["passed"]]
    blockers = []
    if not records:
        blockers.append("no named metal objects found")
    if len(ring_bands) != 1:
        blockers.append("exactly one ring band is required")
    if invalid:
        blockers.append("invalid closed solids or naked edges")
    if records and len(components) != 1:
        blockers.append("metal objects form disconnected contact groups")

    status = (
        "METAL_UNION_BLOCKED"
        if blockers
        else "METAL_UNION_REVIEW_REQUIRED"
    )
    report = {
        "generator": "ptr-metal-union-readiness-v1",
        "status": status,
        "contact_tolerance_mm": CONTACT_TOLERANCE_MM,
        "metal_object_count": len(records),
        "ring_band_count": len(ring_bands),
        "objects": records,
        "contacts": contacts,
        "connected_components": components,
        "blockers": blockers,
        "manual_intersection_review_required": True,
        "production_export_allowed": False,
        "boolean_executed": False,
        "geometry_modified": False,
    }

    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("METAL UNION AUDIT | status=" + status)
    print("METAL OBJECTS | count=" + str(len(records)))
    print("RING BANDS | count=" + str(len(ring_bands)))
    print("CONTACT GROUPS | count=" + str(len(components)))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    print("MANUAL INTERSECTION REVIEW | REQUIRED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("AUDIT JSON | " + REPORT_PATH)
    print("No geometry was modified.")


if __name__ == "__main__":
    main()
'''


def build_metal_union_script(report_path: Path) -> str:
    """Build the IronPython-compatible Rhino audit script."""
    report_literal = json.dumps(str(report_path).replace("\\", "/"))
    return _SCRIPT_TEMPLATE.replace("__REPORT_PATH__", report_literal)


def prepare_metal_union_validator(
    memory_root: Path, now: datetime | None = None
) -> tuple[Path, Path, str]:
    """Return output paths and generated script content."""
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    report_dir = memory_root / "Metal_Union_Audits"
    script_path = script_dir / f"{timestamp}_metal_union_check.py"
    report_path = report_dir / f"{timestamp}_metal_union_readiness.json"
    return script_path, report_path, build_metal_union_script(report_path)


def save_metal_union_validator(script_path: Path, script: str) -> None:
    """Persist a generated Rhino validator."""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script, encoding="utf-8")
