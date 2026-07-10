"""Configuration objects for the PTR-AI Rhino pavé generator."""

from dataclasses import dataclass
from typing import Tuple


# Stores user-editable defaults for pavé layout generation.
@dataclass
class PaveGeneratorSettings:
    """Define safe default parameters for Rhino pavé layout previews."""

    stone_diameter_mm: float = 1.2
    spacing_mm: float = 0.08
    edge_margin_mm: float = 0.45
    layout: str = "staggered"
    preview_layer_name: str = "PTR-AI Pavé Preview"
    preview_color_rgb: Tuple[int, int, int] = (80, 180, 255)

    def validate(self) -> None:
        """Raise a ValueError when default dimensions are not usable."""
        if self.stone_diameter_mm <= 0:
            raise ValueError("stone_diameter_mm must be greater than zero.")
        if self.spacing_mm < 0:
            raise ValueError("spacing_mm cannot be negative.")
        if self.edge_margin_mm < 0:
            raise ValueError("edge_margin_mm cannot be negative.")
        if self.layout not in {"grid", "staggered"}:
            raise ValueError("layout must be either 'grid' or 'staggered'.")
