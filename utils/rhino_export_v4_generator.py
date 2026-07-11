"""Rhino setting v4: strict audit report and guarded 3DM export."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from utils.rhino_setting_v3_generator import build_rhino_setting_v3_script


GENERATOR_VERSION = "ptr-rhino-export-v4"


def build_rhino_export_v4_script(
    report: dict[str, Any],
    output_3dm: Path,
    output_audit_json: Path,
) -> str:
    """Upgrade v3 with RhinoCommon naked-edge checks and guarded SaveAs."""
    script = build_rhino_setting_v3_script(report)
    script = script.replace("ptr-rhino-setting-v3", GENERATOR_VERSION)
    script = script.replace(
        "import rhinoscriptsyntax as rs",
        "import json\nimport os\nimport Rhino\nimport scriptcontext as sc\nimport rhinoscriptsyntax as rs",
    )

    audit_code = r'''

def flatten_object_ids(objects):
    flat = []
    for obj in objects:
        if isinstance(obj, (list, tuple)):
            flat.extend(flatten_object_ids(obj))
        else:
            flat.append(obj)
    return flat


def production_audit(objects):
    rows = []
    can_export = True
    for obj in flatten_object_ids(objects):
        if not obj or not rs.IsObject(obj):
            can_export = False
            continue
        name = rs.ObjectName(obj) or "UNNAMED"
        rhino_object = sc.doc.Objects.FindId(obj)
        brep = Rhino.Geometry.Brep.TryConvertBrep(rhino_object.Geometry) if rhino_object else None
        closed = bool(brep and brep.IsSolid)
        naked_count = None
        if brep:
            naked_curves = brep.DuplicateNakedEdgeCurves(True, True)
            naked_count = len(naked_curves) if naked_curves else 0
        passed = bool(closed and naked_count == 0)
        if not passed:
            can_export = False
        rows.append({
            "name": name,
            "closed_solid": closed,
            "naked_edge_count": naked_count,
            "passed": passed,
        })
        print(
            "V4 AUDIT | " + name
            + " | closed=" + str(closed)
            + " | naked_edges=" + str(naked_count)
            + " | passed=" + str(passed)
        )
    return can_export, rows
'''
    script = script.replace("\ndef main():", audit_code + "\n\ndef main():")

    output_3dm_text = str(output_3dm).replace("\\", "/")
    output_json_text = str(output_audit_json).replace("\\", "/")
    guarded_export = f'''
        # Strict RhinoCommon audit and guarded unique-file export.
        can_export, audit_rows = production_audit(created)
        audit_payload = {{
            "generator": "{GENERATOR_VERSION}",
            "ruleset": "{report["ruleset_version"]}",
            "can_export_3dm": can_export,
            "objects": audit_rows,
            "output_3dm": r"{output_3dm_text}",
        }}
        audit_folder = os.path.dirname(r"{output_json_text}")
        if audit_folder and not os.path.exists(audit_folder):
            os.makedirs(audit_folder)
        with io.open(r"{output_json_text}", "w", encoding="utf-8") as audit_file:
            json.dump(audit_payload, audit_file, ensure_ascii=False, indent=2)

        if can_export:
            export_folder = os.path.dirname(r"{output_3dm_text}")
            if export_folder and not os.path.exists(export_folder):
                os.makedirs(export_folder)
            rs.Command('_-SaveAs "' + r"{output_3dm_text}" + '" _Enter', False)
            print("V4 EXPORT SAVED | {output_3dm_text}")
        else:
            print("V4 EXPORT BLOCKED | inspect audit JSON: {output_json_text}")
'''
    script = script.replace(
        '        rs.SelectObjects(created)\n        rs.ZoomSelected()',
        guarded_export + '\n        rs.SelectObjects(created)\n        rs.ZoomSelected()',
    )
    script = script.replace(
        "PTR setting v3 review concept created. Inspect guides and audit before production.",
        "PTR v4 audit finished. 3DM saves only when every audited object passes.",
    )
    return script


def prepare_v4_paths(memory_root: Path) -> tuple[Path, Path, Path]:
    """Return unique script, 3DM, and audit JSON paths."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    export_dir = memory_root / "Rhino_Exports"
    audit_dir = memory_root / "Rhino_Audits"
    for folder in (script_dir, export_dir, audit_dir):
        folder.mkdir(parents=True, exist_ok=True)
    return (
        script_dir / f"{stamp}_export_v4.py",
        export_dir / f"{stamp}_ring_v4.3dm",
        audit_dir / f"{stamp}_ring_v4_audit.json",
    )


def save_v4_script(path: Path, script: str) -> str:
    path.write_text(script, encoding="utf-8")
    return str(path)
