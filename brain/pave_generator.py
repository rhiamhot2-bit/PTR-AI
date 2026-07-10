"""Pavé planning engine for PTR-AI.

This module estimates simple round-stone pavé layouts on a rectangular
planning area. It does not connect to Rhino, MatrixGold, or generate CAD files.
"""

import math


class PaveGenerator:
    """Create basic straight or staggered pavé layout plans."""

    SUPPORTED_LAYOUTS = {"straight", "staggered"}

    def create_pave_plan(
        self,
        area_width,
        area_length,
        stone_size=1.2,
        gap=0.08,
        edge_margin=0.3,
        layout="staggered",
    ):
        """Return a planning dictionary for a rectangular pavé area.

        All dimensions are in millimeters.

        Args:
            area_width: Width of the pavé area.
            area_length: Length of the pavé area.
            stone_size: Diameter of each round stone.
            gap: Edge-to-edge gap between neighboring stones.
            edge_margin: Clear margin from each area edge to the nearest stone.
            layout: ``straight`` or ``staggered``.
        """
        width = self._positive_number(area_width, "area_width")
        length = self._positive_number(area_length, "area_length")
        diameter = self._positive_number(stone_size, "stone_size")
        spacing = self._non_negative_number(gap, "gap")
        margin = self._non_negative_number(edge_margin, "edge_margin")
        normalized_layout = str(layout).strip().lower()

        if normalized_layout not in self.SUPPORTED_LAYOUTS:
            return {
                "status": "unsupported_layout",
                "layout": layout,
                "supported_layouts": sorted(self.SUPPORTED_LAYOUTS),
                "estimated_stone_count": 0,
                "algorithm": "Pavé Generator V1 rectangular grid planning",
                "note": "Supported layouts are straight and staggered.",
            }

        usable_width = width - (2 * margin)
        usable_length = length - (2 * margin)
        center_distance = diameter + spacing

        if usable_width < diameter or usable_length < diameter:
            return {
                "status": "area_too_small",
                "area_width": width,
                "area_length": length,
                "stone_size": diameter,
                "gap": spacing,
                "edge_margin": margin,
                "layout": normalized_layout,
                "usable_width": max(usable_width, 0.0),
                "usable_length": max(usable_length, 0.0),
                "center_distance": center_distance,
                "row_count": 0,
                "stones_per_full_row": 0,
                "estimated_stone_count": 0,
                "algorithm": "Pavé Generator V1 rectangular grid planning",
                "note": "The usable area cannot fit one complete stone.",
            }

        columns = self._fit_count(usable_width, diameter, center_distance)
        rows = self._fit_count(usable_length, diameter, center_distance)

        if normalized_layout == "straight":
            estimated_stone_count = rows * columns
            short_row_columns = columns
        else:
            short_row_columns = self._fit_staggered_row_count(
                usable_width, diameter, center_distance
            )
            full_rows = math.ceil(rows / 2)
            short_rows = rows // 2
            estimated_stone_count = (
                full_rows * columns + short_rows * short_row_columns
            )

        coverage_width = diameter + max(columns - 1, 0) * center_distance
        coverage_length = diameter + max(rows - 1, 0) * center_distance

        warnings = []
        if spacing < 0.05:
            warnings.append(
                "Gap is below 0.05 mm; verify casting, setting, and metal bridge limits."
            )
        if margin < 0.2:
            warnings.append(
                "Edge margin is below 0.20 mm; verify edge strength before production."
            )

        return {
            "status": "planned",
            "area_width": width,
            "area_length": length,
            "stone_size": diameter,
            "gap": spacing,
            "edge_margin": margin,
            "layout": normalized_layout,
            "usable_width": usable_width,
            "usable_length": usable_length,
            "center_distance": center_distance,
            "row_count": rows,
            "stones_per_full_row": columns,
            "stones_per_short_row": short_row_columns,
            "estimated_stone_count": estimated_stone_count,
            "estimated_coverage_width": coverage_width,
            "estimated_coverage_length": coverage_length,
            "warnings": warnings,
            "algorithm": "Pavé Generator V1 rectangular grid planning",
            "note": (
                "Planning estimate only. Curved surfaces, prongs, cutters, Rhino, "
                "MatrixGold, and CAD generation are not connected yet."
            ),
        }

    @staticmethod
    def _fit_count(usable_size, stone_size, center_distance):
        return math.floor((usable_size - stone_size) / center_distance) + 1

    @staticmethod
    def _fit_staggered_row_count(usable_width, stone_size, center_distance):
        shifted_width = usable_width - (center_distance / 2)
        if shifted_width < stone_size:
            return 0
        return math.floor((shifted_width - stone_size) / center_distance) + 1

    @staticmethod
    def _positive_number(value, field_name):
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be a number") from exc
        if number <= 0:
            raise ValueError(f"{field_name} must be greater than 0")
        return number

    @staticmethod
    def _non_negative_number(value, field_name):
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} must be a number") from exc
        if number < 0:
            raise ValueError(f"{field_name} must be 0 or greater")
        return number
