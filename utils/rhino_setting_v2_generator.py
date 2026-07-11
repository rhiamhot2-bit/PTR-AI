"""Rhino 8 concept generator v2: ring, seat, basket supports, and four prongs."""

from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
from typing import Any


GENERATOR_VERSION = "ptr-rhino-setting-v2"


def build_rhino_setting_v2_script(report: dict[str, Any]) -> str:
    if report["overall_status"] != "ready_for_rhino":
        raise ValueError("CAD check must be ready_for_rhino before script generation.")

    brief = report["brief"]
    values = report["engineering_values"]
    size = float(brief["ring_size"])
    stone = brief["center_stone"]
    length = float(stone["length_mm"])
    width = float(stone["width_mm"])
    depth = max(1.0, width * 0.6)
    shank_w = float(values["shank_width_mm"])
    shank_t = float(values["shank_thickness_mm"])
    prong_d = float(values["prong_diameter_mm"])
    clearance = float(values["seat_clearance_mm"])
    head_h = float(values["head_height_mm"])
    inner_r = (size / math.pi) / 2.0
    major_r = inner_r + shank_t / 2.0
    minor_r = shank_t / 2.0
    seat_y = major_r + minor_r + max(1.0, head_h - depth / 2.0)
    stone_y = seat_y + depth / 2.0
    prong_x = max(0.5, length / 2.0 - prong_d / 2.0)
    prong_z = max(0.5, width / 2.0 - prong_d / 2.0)
    prong_bottom = seat_y - 0.8
    prong_top = stone_y + depth / 2.0 + 0.6
    support_bottom_y = major_r + minor_r * 0.6

    return f'''# PTR JEW3D Rhino 8 Setting Concept
# Generator: {GENERATOR_VERSION}
# Ruleset: {report["ruleset_version"]}
# REVIEW REQUIRED - concept geometry, not production-ready.
import rhinoscriptsyntax as rs


def layer(name, color):
    if not rs.IsLayer(name):
        rs.AddLayer(name, color)
    return name


def cylinder_between(a, b, radius, name):
    obj = rs.AddCylinder(a, b, radius, True)
    if obj:
        rs.ObjectName(obj, name)
    return obj


def main():
    rs.EnableRedraw(False)
    created = []
    try:
        metal = layer("PTR_METAL", (212, 175, 55))
        setting = layer("PTR_SETTING_CONCEPT", (230, 190, 70))
        stone_layer = layer("PTR_STONE_PLACEHOLDER", (0, 160, 90))
        notes = layer("PTR_NOTES", (220, 220, 220))

        rs.CurrentLayer(metal)
        ring = rs.AddTorus((0, 0, 0), {major_r:.6f}, {minor_r:.6f})
        rs.ScaleObject(ring, (0, 0, 0), (1, 1, {shank_w / shank_t:.6f}))
        rs.ObjectName(ring, "PTR_RING_BAND_SIZE_{size:g}")
        created.append(ring)

        rs.CurrentLayer(setting)
        seat_plane = rs.PlaneFromNormal((0, {seat_y:.6f}, 0), (0, 1, 0))
        seat_curve = rs.AddEllipse(
            seat_plane,
            {length / 2.0 + clearance:.6f},
            {width / 2.0 + clearance:.6f},
        )
        seat = rs.AddPipe(seat_curve, 0, {max(0.35, prong_d / 2.0):.6f}, 2, 2)
        rs.DeleteObject(seat_curve)
        if seat:
            rs.ObjectName(seat, "PTR_OVAL_STONE_SEAT_CONCEPT")
            created.append(seat)

        prong_points = [
            (-{prong_x:.6f}, -{prong_z:.6f}),
            (-{prong_x:.6f}, {prong_z:.6f}),
            ({prong_x:.6f}, -{prong_z:.6f}),
            ({prong_x:.6f}, {prong_z:.6f}),
        ]
        for index, (x, z) in enumerate(prong_points, 1):
            obj = cylinder_between(
                (x, {prong_bottom:.6f}, z),
                (x, {prong_top:.6f}, z),
                {prong_d / 2.0:.6f},
                "PTR_PRONG_" + str(index),
            )
            if obj:
                created.append(obj)

        for index, x in enumerate((-{length * 0.3:.6f}, {length * 0.3:.6f}), 1):
            obj = cylinder_between(
                (x, {support_bottom_y:.6f}, 0),
                (x, {seat_y:.6f}, 0),
                {max(0.45, prong_d * 0.65):.6f},
                "PTR_BASKET_SUPPORT_" + str(index),
            )
            if obj:
                created.append(obj)

        rs.CurrentLayer(stone_layer)
        gem = rs.AddSphere((0, {stone_y:.6f}, 0), 1)
        rs.ScaleObject(gem, (0, {stone_y:.6f}, 0), ({length / 2:.6f}, {depth / 2:.6f}, {width / 2:.6f}))
        rs.ObjectName(gem, "PTR_STONE_PLACEHOLDER_{length:g}x{width:g}")
        created.append(gem)

        rs.CurrentLayer(notes)
        rs.AddText(
            "PTR Setting v2 concept | EU {size:g} | professional review required",
            (0, 0, -{shank_w + 3:.6f}),
            1,
        )
        rs.SelectObjects(created)
        rs.ZoomSelected()
        print("PTR setting v2 concept created. Inspect before production.")
    finally:
        rs.EnableRedraw(True)


if __name__ == "__main__":
    main()
'''


def save_rhino_setting_v2_script(memory_root: Path, script: str) -> str:
    folder = memory_root / "Rhino_Scripts"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f_setting_v2.py")
    path.write_text(script, encoding="utf-8")
    return str(path)
