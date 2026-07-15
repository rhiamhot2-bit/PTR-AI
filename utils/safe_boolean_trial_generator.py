"""Generate a non-destructive staged Boolean trial for Rhino 8."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


GENERATOR_VERSION = "ptr-safe-boolean-trial-v1"


def prepare_safe_boolean_trial_paths(memory_root: Path) -> tuple[Path, Path]:
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    audit_dir = memory_root / "Boolean_Trials"
    script_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    return (
        script_dir / f"{stamp}_safe_boolean_trial.py",
        audit_dir / f"{stamp}_safe_boolean_trial.json",
    )


def build_safe_boolean_trial_script(output_audit_json: Path) -> str:
    output_text = str(output_audit_json).replace("\\", "/")
    return f'''# -*- coding: utf-8 -*-
# PTR JEW3D Rhino 8 Safe Boolean Trial
# Generator: {GENERATOR_VERSION}
# NON-DESTRUCTIVE: source objects are never deleted, moved, renamed, or replaced.
import io
import json
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_AUDIT = r"{output_text}"
GENERATOR = "{GENERATOR_VERSION}"
TRIAL_LAYER = "PTR_BOOLEAN_TRIAL"
EXCLUDED_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "NOTE", "BOOLEAN_TRIAL")

STAGES = (
    ("BAND_SHOULDERS", ("RING_BAND", "SHOULDER_LEFT", "SHOULDER_RIGHT")),
    ("SETTING_METAL", ("STONE_SEAT", "PRONG", "BASKET_SUPPORT")),
)


def object_brep(obj_id):
    obj = sc.doc.Objects.FindId(obj_id)
    if not obj:
        return None
    return Rhino.Geometry.Brep.TryConvertBrep(obj.Geometry)


def naked_edge_count(brep):
    curves = brep.DuplicateNakedEdgeCurves(True, True) if brep else None
    return len(curves) if curves else 0


def validate_brep(brep):
    naked = naked_edge_count(brep)
    return {{
        "valid_brep": bool(brep and brep.IsValid),
        "closed_solid": bool(brep and brep.IsSolid),
        "naked_edge_count": naked,
        "passed": bool(brep and brep.IsValid and brep.IsSolid and naked == 0),
    }}


def collect_sources():
    rows = []
    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or ""
        upper = name.upper()
        if any(marker in upper for marker in EXCLUDED_MARKERS):
            continue
        brep = object_brep(obj_id)
        if brep:
            rows.append({{"id": obj_id, "name": name, "upper": upper, "brep": brep}})
    return rows


def add_review_brep(brep, name):
    obj_id = sc.doc.Objects.AddBrep(brep.DuplicateBrep())
    if obj_id:
        rs.ObjectLayer(obj_id, TRIAL_LAYER)
        rs.ObjectName(obj_id, name)
    return obj_id


def run_union(label, inputs, tolerance):
    report = {{"stage": label, "input_count": len(inputs), "passed": False}}
    if len(inputs) < 2:
        report["error"] = "ต้องมีอย่างน้อย 2 ชิ้นสำหรับ Boolean Union"
        return None, report
    try:
        results = Rhino.Geometry.Brep.CreateBooleanUnion(
            [item.DuplicateBrep() for item in inputs], tolerance
        )
    except Exception as exc:
        report["error"] = str(exc)
        return None, report
    report["result_count"] = len(results) if results else 0
    if not results or len(results) != 1:
        report["error"] = "Boolean ต้องคืนผลลัพธ์ Closed Solid เพียง 1 ชิ้น"
        return None, report
    result = results[0]
    report.update(validate_brep(result))
    if report["passed"]:
        add_review_brep(result, "PTR_BOOLEAN_TRIAL_" + label)
        return result, report
    report["error"] = "ผลลัพธ์ไม่ผ่าน Valid Brep / Closed Solid / Naked Edges"
    return None, report


def main():
    if not rs.IsLayer(TRIAL_LAYER):
        rs.AddLayer(TRIAL_LAYER, color=(255, 128, 0))
    sources = collect_sources()
    tolerance = max(float(sc.doc.ModelAbsoluteTolerance), 0.001)
    source_names = [row["name"] for row in sources]
    reports = []
    stage_results = []

    for label, markers in STAGES:
        selected = [
            row for row in sources
            if any(marker in row["upper"] for marker in markers)
        ]
        for row in selected:
            add_review_brep(row["brep"], "PTR_BOOLEAN_TRIAL_SOURCE_" + row["name"])
        result, report = run_union(label, [row["brep"] for row in selected], tolerance)
        report["source_names"] = [row["name"] for row in selected]
        reports.append(report)
        if result:
            stage_results.append(result)

    final_result = None
    final_report = {{"stage": "FINAL_ASSEMBLY", "passed": False}}
    if len(stage_results) == len(STAGES):
        final_result, final_report = run_union("FINAL_ASSEMBLY", stage_results, tolerance)
    else:
        final_report["error"] = "หยุดก่อน Final Boolean เพราะมี Stage ไม่ผ่าน"
    reports.append(final_report)

    all_passed = bool(final_result and final_report.get("passed"))
    payload = {{
        "generator": GENERATOR,
        "status": "BOOLEAN_TRIAL_PASSED_REVIEW_REQUIRED" if all_passed else "BOOLEAN_TRIAL_BLOCKED",
        "source_geometry_modified": False,
        "production_export_allowed": False,
        "trial_layer": TRIAL_LAYER,
        "tolerance_mm": tolerance,
        "excluded_markers": list(EXCLUDED_MARKERS),
        "source_names": source_names,
        "stages": reports,
        "all_stages_passed": all_passed,
    }}
    folder = os.path.dirname(OUTPUT_AUDIT)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with io.open(OUTPUT_AUDIT, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)

    for report in reports:
        print("SAFE BOOLEAN | {0} | passed={1} | results={2}".format(
            report["stage"], report.get("passed", False), report.get("result_count", 0)
        ))
        if report.get("error"):
            print("BLOCKER | " + report["error"])
    print("SOURCE GEOMETRY MODIFIED | NO")
    print("PRODUCTION EXPORT | BLOCKED")
    print("BOOLEAN TRIAL JSON | " + OUTPUT_AUDIT)
    sc.doc.Views.Redraw()


if __name__ == "__main__":
    main()
'''


def save_safe_boolean_trial_script(path: Path, script: str) -> str:
    path.write_text(script, encoding="utf-8")
    return str(path)
