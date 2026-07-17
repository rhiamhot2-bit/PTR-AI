"""Generate a report-only Rhino metal contact gap analyzer."""

from datetime import datetime
import json
from pathlib import Path

GENERATOR_ID = "ptr-metal-contact-gap-analyzer-v1"
CONTACT_TOLERANCE_MM = 0.05
NEAR_TOLERANCE_MM = 0.50
BRIDGE_ALLOWANCE_MM = 0.10

_SOURCE_MARKERS = (
    "RING_BAND",
    "STONE_SEAT",
    "PRONG",
    "BASKET_SUPPORT",
    "SHOULDER",
    "PRODUCTION_METAL",
)
_EXCLUDED_MARKERS = (
    "STONE_PLACEHOLDER",
    "GIRDLE",
    "GUIDE",
    "NOTE",
    "TEXT",
    "REHEARSAL",
    "TRIAL",
    "COPY",
)


def is_source_metal_name(name: str) -> bool:
    """Return True only for named production-metal candidates."""
    normalized = (name or "").upper()
    return (
        any(marker in normalized for marker in _SOURCE_MARKERS)
        and not any(marker in normalized for marker in _EXCLUDED_MARKERS)
    )


def bbox_gap_mm(first, second) -> float:
    """Return Euclidean separation between two axis-aligned bounding boxes."""
    gaps = []
    for axis in range(3):
        gaps.append(max(0.0, second[0][axis] - first[1][axis], first[0][axis] - second[1][axis]))
    return sum(gap * gap for gap in gaps) ** 0.5


def classify_gap_mm(gap_mm: float) -> str:
    if gap_mm <= CONTACT_TOLERANCE_MM:
        return "contact"
    if gap_mm <= NEAR_TOLERANCE_MM:
        return "near"
    return "disconnected"


def build_metal_contact_gap_script(report_path: Path) -> str:
    """Build a Rhino-compatible, read-only contact-gap audit script."""
    template = r'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Metal Contact Gap Analyzer
# Generator: ptr-metal-contact-gap-analyzer-v1
# REPORT ONLY: bounding-box screening; never modifies or exports geometry.
import io
import json
import math
import os
import rhinoscriptsyntax as rs

REPORT_PATH = __REPORT_PATH__
CONTACT_TOLERANCE_MM = 0.05
NEAR_TOLERANCE_MM = 0.50
BRIDGE_ALLOWANCE_MM = 0.10
SOURCE_MARKERS = ("RING_BAND", "STONE_SEAT", "PRONG", "BASKET_SUPPORT", "SHOULDER", "PRODUCTION_METAL")
EXCLUDED_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE", "GUIDE", "NOTE", "TEXT", "REHEARSAL", "TRIAL", "COPY")


def source_name(name):
    value = (name or "").upper()
    return any(marker in value for marker in SOURCE_MARKERS) and not any(marker in value for marker in EXCLUDED_MARKERS)


def object_box(object_id):
    corners = rs.BoundingBox(object_id)
    if not corners:
        return None
    values = [(point.X, point.Y, point.Z) for point in corners]
    return {
        "min": [min(point[i] for point in values) for i in range(3)],
        "max": [max(point[i] for point in values) for i in range(3)],
    }


def gap_between(first, second):
    gaps = [
        max(0.0, second["min"][i] - first["max"][i], first["min"][i] - second["max"][i])
        for i in range(3)
    ]
    return math.sqrt(sum(value * value for value in gaps))


def gap_class(gap):
    if gap <= CONTACT_TOLERANCE_MM:
        return "contact"
    if gap <= NEAR_TOLERANCE_MM:
        return "near"
    return "disconnected"


def connected_components(names, adjacency):
    remaining = set(names)
    components = []
    while remaining:
        stack = [remaining.pop()]
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def main():
    objects = []
    for object_id in rs.AllObjects() or []:
        name = rs.ObjectName(object_id) or ""
        if source_name(name):
            box = object_box(object_id)
            if box:
                objects.append({"name": name, "bbox": box})

    names = [item["name"] for item in objects]
    adjacency = dict((name, set()) for name in names)
    pairs = []
    closest_bridge = None

    for index, first in enumerate(objects):
        for second in objects[index + 1:]:
            gap = gap_between(first["bbox"], second["bbox"])
            classification = gap_class(gap)
            pair = {
                "first": first["name"],
                "second": second["name"],
                "gap_mm": round(gap, 4),
                "classification": classification,
            }
            pairs.append(pair)
            if classification in ("contact", "near"):
                adjacency[first["name"]].add(second["name"])
                adjacency[second["name"]].add(first["name"])

    components = connected_components(names, adjacency)
    component_index = {}
    for index, component in enumerate(components):
        for name in component:
            component_index[name] = index

    for pair in pairs:
        if component_index.get(pair["first"]) != component_index.get(pair["second"]):
            if closest_bridge is None or pair["gap_mm"] < closest_bridge["gap_mm"]:
                closest_bridge = dict(pair)
                closest_bridge["suggested_extension_mm"] = round(pair["gap_mm"] + BRIDGE_ALLOWANCE_MM, 4)

    report = {
        "generator": "ptr-metal-contact-gap-analyzer-v1",
        "status": "METAL_CONTACT_GAP_REVIEW_REQUIRED",
        "method": "axis_aligned_bounding_box_screening_only",
        "contact_tolerance_mm": CONTACT_TOLERANCE_MM,
        "near_tolerance_mm": NEAR_TOLERANCE_MM,
        "objects": names,
        "pairs": pairs,
        "connected_components": components,
        "closest_component_bridge": closest_bridge,
        "original_geometry_modified": False,
        "production_export": "BLOCKED",
        "professional_review_required": True,
        "warning": "Bounding-box proximity is not proof of surface contact or manufacturability.",
    }
    folder = os.path.dirname(REPORT_PATH)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with io.open(REPORT_PATH, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print("METAL CONTACT GAP ANALYZER | status=METAL_CONTACT_GAP_REVIEW_REQUIRED")
    print("SOURCE METAL OBJECTS | count={0}".format(len(objects)))
    print("CONNECTED COMPONENTS | count={0}".format(len(components)))
    for pair in pairs:
        print("GAP | {0} <-> {1} | {2} mm | {3}".format(
            pair["first"], pair["second"], pair["gap_mm"], pair["classification"]))
    if closest_bridge:
        print("CLOSEST BRIDGE | {0} <-> {1} | suggested_extension_mm={2}".format(
            closest_bridge["first"], closest_bridge["second"], closest_bridge["suggested_extension_mm"]))
    print("BOUNDING-BOX SCREENING ONLY | PROFESSIONAL JEWELRY-CAD REVIEW REQUIRED")
    print("PRODUCTION EXPORT | BLOCKED")
    print("ORIGINAL GEOMETRY MODIFIED | NO")
    print("AUDIT JSON | {0}".format(REPORT_PATH))


if __name__ == "__main__":
    main()
'''
    return template.replace("__REPORT_PATH__", json.dumps(str(report_path)))


def prepare_metal_contact_gap_analyzer(memory_root: Path, now=None):
    timestamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S-%f")
    report_dir = Path(memory_root) / "Metal_Contact_Gaps"
    report_dir.mkdir(parents=True, exist_ok=True)
    script_path = report_dir / f"{timestamp}_metal_contact_gaps.py"
    report_path = report_dir / f"{timestamp}_metal_contact_gaps.json"
    return script_path, report_path, build_metal_contact_gap_script(report_path)


def save_metal_contact_gap_analyzer(script_path: Path, script: str) -> None:
    script_path.write_text(script, encoding="utf-8")
