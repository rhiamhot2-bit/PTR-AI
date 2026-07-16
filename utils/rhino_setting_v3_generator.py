"""Rhino setting v3: refined prong concept, girdle guides, and geometry audit."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from utils.rhino_setting_v2_generator import build_rhino_setting_v2_script


GENERATOR_VERSION = "ptr-rhino-setting-v3"


def build_rhino_setting_v3_script(report: dict[str, Any]) -> str:
    """Upgrade the validated v2 concept script with v3 review features."""
    script = build_rhino_setting_v2_script(report)
    brief = report["brief"]
    values = report["engineering_values"]
    length = float(brief["center_stone"]["length_mm"])
    width = float(brief["center_stone"]["width_mm"])
    prong_d = float(values["prong_diameter_mm"])

    script = script.replace("ptr-rhino-setting-v2", GENERATOR_VERSION)
    # Use an explicit seat plane frame so the oval axes always match the stone axes.
    script = script.replace(
        'rs.PlaneFromNormal((0, {seat_y:.6f}, 0), (0, 1, 0))'.format(
            seat_y=_geometry(report)[0]
        ),
        'rs.PlaneFromFrame((0, {seat_y:.6f}, 0), (1, 0, 0), (0, 0, 1))'.format(
            seat_y=_geometry(report)[0]
        ),
    )
    script = script.replace(
        "# REVIEW REQUIRED - concept geometry, not production-ready.",
        "# REVIEW REQUIRED - v3 review geometry, not production-ready.",
    )

    audit_function = '''

def geometry_audit(objects):
    results = []
    for obj in objects:
        if not obj or not rs.IsObject(obj):
            continue
        name = rs.ObjectName(obj) or "UNNAMED"
        closed = rs.IsObjectSolid(obj)
        results.append((name, bool(closed)))
        print("GEOMETRY AUDIT | " + name + " | closed solid: " + str(bool(closed)))
    return results
'''
    script = script.replace("\ndef main():", audit_function + "\n\ndef main():")

    # Flare each prong tip slightly outward while its base remains embedded in the seat.
    old_end = "                (x, {top}, z),".format(
        top=_prong_top(report),
    )
    new_end = "                (x * 1.08, {top}, z * 1.08),".format(
        top=_prong_top(report),
    )
    script = script.replace(old_end, new_end)

    guides = f'''
        # Non-Boolean girdle guide cutters. These mark proposed notch locations only.
        guide_layer = layer("PTR_GIRDLE_GUIDES", (220, 60, 60))
        rs.CurrentLayer(guide_layer)
        guide_radius = {max(0.18, prong_d * 0.32):.6f}
        for index, (x, z) in enumerate(prong_points, 1):
            guide = rs.AddSphere((x * 0.94, {_stone_center_y(report):.6f}, z * 0.94), guide_radius)
            if guide:
                rs.ObjectName(guide, "PTR_GIRDLE_GUIDE_" + str(index))
                created.append(guide)

        # Jewelry orientation: rotate the complete assembly from XY into XZ.
        # Front now shows the full ring; Top shows the setting profile.
        rs.RotateObjects(created, (0, 0, 0), 90.0, (1, 0, 0), False)

        # Align the complete setting head with the finger direction.
        # Keep the ring fixed; rotate seat, stone, prongs, basket, and guides together.
        head_objects = []
        for layer_name in (
            "PTR_SETTING_CONCEPT",
            "PTR_STONE_PLACEHOLDER",
            "PTR_GIRDLE_GUIDES",
        ):
            layer_objects = rs.ObjectsByLayer(layer_name) or []
            head_objects.extend(layer_objects)
        rs.RotateObjects(head_objects, (0, 0, 0), 90.0, (0, 0, 1), False)

        # Geometry audit reports closed solids but does not Boolean union anything.
        audit = geometry_audit(created)
        rs.CurrentLayer(notes)
        rs.AddText(
            "V3 audit: " + str(sum(1 for item in audit if item[1]))
            + "/" + str(len(audit)) + " closed solids | manual Boolean required",
            (0, 0, -{width + 5.0:.6f}),
            1,
        )
'''
    script = script.replace("        rs.CurrentLayer(notes)\n        rs.AddText(", guides + "\n        rs.CurrentLayer(notes)\n        rs.AddText(")
    script = script.replace(
        "PTR setting v2 concept created. Inspect before production.",
        "PTR setting v3 review concept created. Inspect guides and audit before production.",
    )
    return script


def _geometry(report: dict[str, Any]) -> tuple[float, float, float, float]:
    import math

    brief = report["brief"]
    values = report["engineering_values"]
    size = float(brief["ring_size"])
    width = float(brief["center_stone"]["width_mm"])
    depth = max(1.0, width * 0.6)
    shank_t = float(values["shank_thickness_mm"])
    head_h = float(values["head_height_mm"])
    major_r = (size / math.pi) / 2.0 + shank_t / 2.0
    minor_r = shank_t / 2.0
    seat_y = major_r + minor_r + max(1.0, head_h - depth / 2.0)
    stone_y = seat_y + depth / 2.0
    return seat_y, stone_y, depth, float(values["prong_diameter_mm"])


def _prong_top(report: dict[str, Any]) -> str:
    _, stone_y, depth, _ = _geometry(report)
    return f"{stone_y + depth / 2.0 + 0.6:.6f}"


def _stone_center_y(report: dict[str, Any]) -> float:
    return _geometry(report)[1]


def save_rhino_setting_v3_script(memory_root: Path, script: str) -> str:
    folder = memory_root / "Rhino_Scripts"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f_setting_v3.py")
    path.write_text(script, encoding="utf-8")
    return str(path)
