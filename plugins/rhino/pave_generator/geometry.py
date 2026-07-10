"""Geometry planning helpers for RhinoCommon-compatible pavé previews.

This module avoids complex placement algorithms for the first plugin structure.
The classes return simple Python data that can later be converted to
Rhino.Geometry objects inside Rhino 8 commands.
"""

from dataclasses import dataclass
from typing import Dict, List

from .settings import PaveGeneratorSettings


# Represents a planned pavé stone center before Rhino geometry is created.
@dataclass(frozen=True)
class PavePoint:
    """Store a stone center and diameter in millimeters."""

    x: float
    y: float
    z: float
    diameter_mm: float

    def as_tuple(self) -> tuple:
        """Return the point as a RhinoCommon-friendly coordinate tuple."""
        return (self.x, self.y, self.z)


# Builds placeholder geometry data for future RhinoCommon object creation.
class PaveGeometryBuilder:
    """Create lightweight pavé preview geometry descriptions."""

    def __init__(self, settings: PaveGeneratorSettings) -> None:
        """Initialize the builder with validated plugin settings."""
        settings.validate()
        self.settings = settings

    def build_preview_points(self, length_mm: float, width_mm: float) -> List[PavePoint]:
        """Return a minimal center-point preview for the requested area.

        The first architecture pass intentionally creates only one center point.
        Full grid, staggered, surface projection, and collision logic will be
        added in later milestones.
        """
        self._validate_area(length_mm, width_mm)
        return [
            PavePoint(
                x=length_mm / 2,
                y=width_mm / 2,
                z=0.0,
                diameter_mm=self.settings.stone_diameter_mm,
            )
        ]

    def describe_preview(self, length_mm: float, width_mm: float) -> Dict[str, object]:
        """Return serializable preview metadata for command and UI layers."""
        points = self.build_preview_points(length_mm, width_mm)
        return {
            "layout": self.settings.layout,
            "stone_count": len(points),
            "points": [point.as_tuple() for point in points],
            "diameter_mm": self.settings.stone_diameter_mm,
            "rhino_common_ready": True,
        }

    def _validate_area(self, length_mm: float, width_mm: float) -> None:
        """Raise a ValueError when preview dimensions are not usable."""
        if length_mm <= 0:
            raise ValueError("length_mm must be greater than zero.")
        if width_mm <= 0:
            raise ValueError("width_mm must be greater than zero.")
