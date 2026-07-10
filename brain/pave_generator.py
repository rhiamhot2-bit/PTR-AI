"""Pavé planning engine for PTR-AI.

This module estimates simple pavé stone layouts only. It does not connect to
Rhino, MatrixGold, or generate any 3D/CAD files.
"""

from math import floor, pi
from typing import Dict, Optional, Union


Number = Union[int, float]
PlanDict = Dict[str, object]


class PaveGenerator:
    """Create simple pavé plans for rectangular or tapered surfaces."""

    SUPPORTED_LAYOUTS = {"grid", "staggered"}
    STAGGERED_VERTICAL_FACTOR = 0.8660254
    ALGORITHM_NAME = "Pavé Generator V1 rectangular / tapered pitch estimate"
    PLANNING_NOTE = (
        "Planning estimate only. No Rhino, MatrixGold, or 3D file generation "
        "is connected yet. Half stones are not added in V1."
    )

    def create_pave_plan(
        self,
        length: Number,
        width_start: Number,
        width_end: Optional[Number] = None,
        stone_size: Number = 1.2,
        gap: Number = 0.08,
        edge_margin: Number = 0.45,
        layout: str = "staggered",
    ) -> PlanDict:
        """Return a planning dictionary for a simple pavé layout.

        Args:
            length: Surface length in millimeters.
            width_start: Surface width at the start in millimeters.
            width_end: Surface width at the end in millimeters. Defaults to
                ``width_start`` for rectangular surfaces.
            stone_size: Pavé stone diameter in millimeters.
            gap: Gap between stones in millimeters.
            edge_margin: Margin from each surface edge in millimeters.
            layout: Supported layout name, either ``"grid"`` or
                ``"staggered"``.
        """
        final_width_end = width_start if width_end is None else width_end
        normalized_layout = self._normalize_layout(layout)

        validation_error = self._validate_inputs(
            length=length,
            width_start=width_start,
            width_end=final_width_end,
            stone_size=stone_size,
            gap=gap,
            edge_margin=edge_margin,
            layout=normalized_layout,
        )
        if validation_error:
            return validation_error

        length_value = float(length)
        width_start_value = float(width_start)
        width_end_value = float(final_width_end)
        stone_size_value = float(stone_size)
        gap_value = float(gap)
        edge_margin_value = float(edge_margin)

        pitch = stone_size_value + gap_value
        usable_length = length_value - (2 * edge_margin_value)
        usable_width_start = width_start_value - (2 * edge_margin_value)
        usable_width_end = width_end_value - (2 * edge_margin_value)
        average_usable_width = (usable_width_start + usable_width_end) / 2

        horizontal_pitch = pitch
        vertical_pitch = self._calculate_vertical_pitch(pitch, normalized_layout)
        columns = floor(usable_length / horizontal_pitch)
        rows = floor(average_usable_width / vertical_pitch)
        estimated_stone_count = columns * rows
        estimated_coverage_percent = self._estimate_coverage_percent(
            estimated_stone_count=estimated_stone_count,
            stone_size=stone_size_value,
            usable_length=usable_length,
            average_usable_width=average_usable_width,
        )

        return {
            "status": "planned",
            "layout": normalized_layout,
            "length": length_value,
            "width_start": width_start_value,
            "width_end": width_end_value,
            "stone_size": stone_size_value,
            "gap": gap_value,
            "edge_margin": edge_margin_value,
            "horizontal_pitch": horizontal_pitch,
            "vertical_pitch": vertical_pitch,
            "usable_length": usable_length,
            "usable_width_start": usable_width_start,
            "usable_width_end": usable_width_end,
            "average_usable_width": average_usable_width,
            "columns": columns,
            "rows": rows,
            "estimated_stone_count": estimated_stone_count,
            "estimated_coverage_percent": estimated_coverage_percent,
            "algorithm": self.ALGORITHM_NAME,
            "note": self.PLANNING_NOTE,
        }

    def _normalize_layout(self, layout: str) -> str:
        return str(layout).strip().lower()

    def _validate_inputs(
        self,
        length: Number,
        width_start: Number,
        width_end: Number,
        stone_size: Number,
        gap: Number,
        edge_margin: Number,
        layout: str,
    ) -> Optional[PlanDict]:
        if layout not in self.SUPPORTED_LAYOUTS:
            return self._error_plan(
                "unsupported_layout",
                layout,
                "Supported layouts are grid and staggered.",
            )

        numeric_values = {
            "length": length,
            "width_start": width_start,
            "width_end": width_end,
            "stone_size": stone_size,
            "gap": gap,
            "edge_margin": edge_margin,
        }
        try:
            values = {key: float(value) for key, value in numeric_values.items()}
        except (TypeError, ValueError):
            return self._error_plan(
                "invalid_numeric_input",
                layout,
                "Length, widths, stone size, gap, and edge margin must be numeric.",
            )

        if (
            values["length"] <= 0
            or values["width_start"] <= 0
            or values["width_end"] <= 0
            or values["stone_size"] <= 0
            or values["gap"] < 0
            or values["edge_margin"] < 0
        ):
            return self._error_plan(
                "invalid_dimension",
                layout,
                "Length, widths, and stone size must be positive; gap and edge margin cannot be negative.",
            )

        usable_length = values["length"] - (2 * values["edge_margin"])
        usable_width_start = values["width_start"] - (2 * values["edge_margin"])
        usable_width_end = values["width_end"] - (2 * values["edge_margin"])
        if usable_length <= 0 or usable_width_start <= 0 or usable_width_end <= 0:
            return self._error_plan(
                "invalid_usable_area",
                layout,
                "Usable length and widths must be greater than zero after edge margins.",
            )

        return None

    def _error_plan(self, status: str, layout: str, note: str) -> PlanDict:
        return {
            "status": status,
            "layout": layout,
            "length": None,
            "width_start": None,
            "width_end": None,
            "stone_size": None,
            "gap": None,
            "edge_margin": None,
            "horizontal_pitch": None,
            "vertical_pitch": None,
            "usable_length": None,
            "usable_width_start": None,
            "usable_width_end": None,
            "average_usable_width": None,
            "columns": 0,
            "rows": 0,
            "estimated_stone_count": 0,
            "estimated_coverage_percent": 0.0,
            "algorithm": self.ALGORITHM_NAME,
            "note": note,
        }

    def _calculate_vertical_pitch(self, pitch: float, layout: str) -> float:
        if layout == "staggered":
            return pitch * self.STAGGERED_VERTICAL_FACTOR
        return pitch

    def _estimate_coverage_percent(
        self,
        estimated_stone_count: int,
        stone_size: float,
        usable_length: float,
        average_usable_width: float,
    ) -> float:
        stone_area = pi * (stone_size / 2) ** 2
        surface_area = usable_length * average_usable_width
        return round((estimated_stone_count * stone_area / surface_area) * 100, 2)
