"""Generate reviewable Rhino 8 Python scripts from validated ring requests."""

from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
from typing import Any


GENERATOR_VERSION = "ptr-rhino-ring-v1"


def ring_inner_diameter_mm(eu_size: float) -> float:
    """Convert EU circumference size to inner diameter in millimeters."""
    return eu_size / math.pi


def build_rhino_ring_script(report: dict[str, Any]) -> str:
    """Return a Rhino 8 Python script for a ring band and stone placeholder."""
    if report["overall_status"] != "ready_for_rhino":
        raise ValueError("CAD check must be ready_for_rhino before script generation.")

    brief = report["brief"]
    values = report["engineering_values"]
    ring_size = brief["ring_size"]
    stone = brief["center_stone"]

    if ring_size is None or stone["length_mm"] is None or stone["width_mm"] is None:
        raise ValueError("Ring size and stone dimensions are required.")

    inner_diameter = ring_inner_diameter_mm(float(ring_size))
    inner_radius = inner_diameter / 2.0
    shank_width = float(values["shank_width_mm"])
    shank_thickness = float(values["shank_thickness_mm"])
    major_radius = inner_radius + (shank_thickness / 2.0)
    minor_radius = shank_thickness / 2.0
    width_scale = shank_width / shank_thickness
    head_height = float(values["head_height_mm"])
    stone_length = float(stone["length_mm"])
    stone_width = float(stone["width_mm"])
    stone_depth = max(1.0, stone_width * 0.6)
    stone_center_y = major_radius + minor_radius + head_height

    return f'''# PTR JEW3D Rhino 8 Script
# Generator: {GENERATOR_VERSION}
# Ruleset: {report["ruleset_version"]}
# REVIEW REQUIRED: This creates concept geometry only. A jewelry CAD professional
# must inspect dimensions, tolerances, manufacturability, and stone setting.
import rhinoscriptsyntax as rs


def ensure_layer(name, color):
    if not rs.IsLayer(name):
        rs.AddLayer(name, color)
    return name


def main():
    rs.EnableRedraw(False)
    try:
        metal_layer = ensure_layer("PTR_METAL", (212, 175, 55))
        stone_layer = ensure_layer("PTR_STONE_PLACEHOLDER", (0, 160, 90))
        note_layer = ensure_layer("PTR_NOTES", (220, 220, 220))

        # EU ring size is treated as inner circumference in millimeters.
        inner_diameter = {inner_diameter:.6f}
        inner_radius = {inner_radius:.6f}
        shank_width = {shank_width:.6f}
        shank_thickness = {shank_thickness:.6f}
        major_radius = {major_radius:.6f}
        minor_radius = {minor_radius:.6f}

        # Torus axis is World Z. Scale Z to create an elliptical shank section.
        rs.CurrentLayer(metal_layer)
        ring = rs.AddTorus((0, 0, 0), major_radius, minor_radius)
        if not ring:
            raise RuntimeError("Could not create ring band.")
        rs.ScaleObject(ring, (0, 0, 0), (1.0, 1.0, {width_scale:.6f}))
        rs.ObjectName(ring, "PTR_RING_BAND_SIZE_{ring_size}")

        # Stone is a non-production ellipsoid placeholder at the ring head.
        rs.CurrentLayer(stone_layer)
        stone = rs.AddSphere((0, {stone_center_y:.6f}, 0), 1.0)
        if not stone:
            raise RuntimeError("Could not create stone placeholder.")
        rs.ScaleObject(
            stone,
            (0, {stone_center_y:.6f}, 0),
            ({stone_length / 2.0:.6f}, {stone_depth / 2.0:.6f}, {stone_width / 2.0:.6f}),
        )
        rs.ObjectName(stone, "PTR_{str(stone["type"] or "STONE").upper()}_{stone_length:g}x{stone_width:g}")

        rs.CurrentLayer(note_layer)
        note = (
            "PTR concept only | EU size {ring_size} | inner diameter "
            + str(round(inner_diameter, 3))
            + " mm | professional review required"
        )
        rs.AddText(note, (0, 0, -({shank_width:.6f} + 3.0)), 1.0)

        rs.SelectObjects([ring, stone])
        rs.ZoomSelected()
        print("PTR Rhino concept created. Review geometry before production.")
    finally:
        rs.EnableRedraw(True)


if __name__ == "__main__":
    main()
'''


def save_rhino_script(
    memory_root: Path,
    report: dict[str, Any],
    script: str,
) -> str:
    """Save a generated Rhino Python script and return its path."""
    folder = memory_root / "Rhino_Scripts"
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    path = folder / now.strftime("%Y-%m-%d_%H-%M-%S-%f_ring_v1.py")
    path.write_text(script, encoding="utf-8")
    return str(path)
