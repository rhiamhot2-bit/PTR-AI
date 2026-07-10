# PTR-AI Rhino Pavé Generator

First Rhino plugin structure for PTR-AI pavé generation.

## Purpose

This package prepares a clean, extensible Rhino 8 plugin architecture for future pavé layout generation. It does **not** implement complex layout, projection, collision, setting, or manufacturing algorithms yet.

## Requirements

- Python 3
- Rhino 8 target environment
- RhinoCommon-compatible geometry boundaries
- No mandatory RhinoCommon import outside Rhino command execution

## Architecture

```text
plugins/rhino/pave_generator/
├── __init__.py          # Package exports
├── pave_generator.py    # High-level plugin coordinator
├── geometry.py          # Geometry planning placeholders
├── settings.py          # User-editable plugin settings
└── README.md            # Plugin documentation
```

## Design Principles

- Keep Rhino command/UI concerns separate from geometry planning.
- Use simple Python data structures until RhinoCommon objects are created inside Rhino.
- Validate settings and dimensions close to the service that uses them.
- Keep classes small so future algorithms can be added without rewriting the plugin shell.

## Current Capabilities

- Exposes plugin metadata for Rhino command integration.
- Validates initial pavé settings.
- Produces a minimal placeholder preview point for architecture testing.
- Marks preview output as RhinoCommon-ready for later conversion to `Rhino.Geometry` objects.

## Future Milestones

- Add Rhino 8 command registration and toolbar/menu integration.
- Convert preview payloads into RhinoCommon curves, points, and surface-aware objects.
- Implement grid and staggered pavé layout algorithms.
- Add surface projection, edge margins, collision checks, and setting geometry.
- Connect generated layouts to PTR-AI planning and manufacturing workflows.
