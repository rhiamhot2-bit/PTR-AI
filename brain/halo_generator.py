"""Halo planning engine for PTR-AI.

This module estimates simple halo stone layouts only. It does not connect to
Rhino, MatrixGold, or generate any 3D/CAD files.
"""


class HaloGenerator:
    """Create simple halo plans for supported center stone shapes."""

    SUPPORTED_SHAPES = {
        "Round",
        "Oval",
        "Pear",
        "Marquise",
        "Emerald",
        "Princess",
        "Heart",
    }

    def create_halo_plan(self, center_shape, center_size, stone_size=1.2, gap=0.08):
        """Return a planning dictionary for a simple halo layout.

        Args:
            center_shape: Center stone shape name.
            center_size: Diameter as a number, or dimensions such as "8x10".
            stone_size: Halo stone diameter in millimeters.
            gap: Gap between halo stones in millimeters.
        """
        normalized_shape = self._normalize_shape(center_shape)
        if normalized_shape not in self.SUPPORTED_SHAPES:
            return {
                "status": "unsupported_center_shape",
                "center_shape": center_shape,
                "center_size": center_size,
                "halo_stone_size": stone_size,
                "gap": gap,
                "center_distance": None,
                "estimated_stone_count": 0,
                "algorithm": "Halo Generator V1 perimeter / center_distance",
                "note": (
                    "Supported center shapes are Round, Oval, Pear, Marquise, "
                    "Emerald, Princess, and Heart."
                ),
            }

        center_distance = stone_size + gap
        perimeter = self._estimate_perimeter(center_size)
        estimated_stone_count = round(perimeter / center_distance)

        return {
            "status": "planned",
            "center_shape": normalized_shape,
            "center_size": center_size,
            "halo_stone_size": stone_size,
            "gap": gap,
            "center_distance": center_distance,
            "estimated_stone_count": estimated_stone_count,
            "algorithm": "Halo Generator V1 perimeter / center_distance",
            "note": (
                "Planning estimate only. No Rhino, MatrixGold, or 3D file "
                "generation is connected yet."
            ),
        }

    def _normalize_shape(self, center_shape):
        return str(center_shape).strip().title()

    def _estimate_perimeter(self, center_size):
        if isinstance(center_size, (int, float)):
            return 3.14159 * float(center_size)

        size_text = str(center_size).strip().lower().replace(" ", "")
        if "x" in size_text:
            width_text, length_text = size_text.split("x", 1)
            width = float(width_text)
            length = float(length_text)
            return 2 * (width + length)

        diameter = float(size_text)
        return 3.14159 * diameter
