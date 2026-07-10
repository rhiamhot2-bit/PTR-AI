"""High-level plugin coordinator for the PTR-AI Rhino pavé generator."""

from typing import Dict, Optional

from .geometry import PaveGeometryBuilder
from .settings import PaveGeneratorSettings


# Coordinates settings and geometry services for Rhino command entry points.
class PaveGeneratorPlugin:
    """Provide the public API used by future Rhino 8 command scripts."""

    PLUGIN_NAME = "PTR-AI Pavé Generator"
    TARGET_RHINO_VERSION = "Rhino 8"

    def __init__(self, settings: Optional[PaveGeneratorSettings] = None) -> None:
        """Initialize plugin services with default or caller-provided settings."""
        self.settings = settings or PaveGeneratorSettings()
        self.settings.validate()
        self.geometry_builder = PaveGeometryBuilder(self.settings)

    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata for menus, logs, and diagnostics."""
        return {
            "name": self.PLUGIN_NAME,
            "target_rhino_version": self.TARGET_RHINO_VERSION,
            "python": "Python 3",
            "geometry_api": "RhinoCommon compatible",
        }

    def create_preview(self, length_mm: float, width_mm: float) -> Dict[str, object]:
        """Create a lightweight pavé preview payload for Rhino command layers."""
        preview = self.geometry_builder.describe_preview(length_mm, width_mm)
        preview["plugin"] = self.get_metadata()
        return preview
