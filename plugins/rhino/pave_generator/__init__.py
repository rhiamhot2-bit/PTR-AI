"""PTR-AI Rhino pavé generator plugin package.

The package is intentionally small for the first plugin milestone. It exposes
settings, geometry planning primitives, and the high-level plugin coordinator
without requiring RhinoCommon at import time outside Rhino.
"""

from .geometry import PaveGeometryBuilder, PavePoint
from .pave_generator import PaveGeneratorPlugin
from .settings import PaveGeneratorSettings

__all__ = [
    "PaveGeneratorPlugin",
    "PaveGeneratorSettings",
    "PaveGeometryBuilder",
    "PavePoint",
]
