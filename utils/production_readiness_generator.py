"""Generate a report-only Rhino 8 production-readiness audit."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


GENERATOR_VERSION = "ptr-production-readiness-v1"


def build_production_readiness_script(output_audit_json: Path) -> str:
    """Return a Rhino script that audits the open document without modifying it."""
    output_text = str(output_audit_json).replace("\\", "/")
    return f'''# PTR JEW3D Rhino 8 Production Readiness Audit
# Generator: {GENERATOR_VERSION}
# REPORT ONLY: this script never Boolean-unions, deletes, or exports geometry.
import io
import json
import os
import Rhino
import scriptcontext as sc
import rhinoscriptsyntax as rs

OUTPUT_AUDIT = r"{output_text}"
GENERATOR = "{GENERATOR_VERSION}"

REFERENCE_MARKERS = ("STONE_PLACEHOLDER", "GIRDLE_GUIDE", "NOTE")
METAL_MARKERS = ("RING_BAND", "STONE_SEAT", "PRONG", "BASKET_SUPPORT", "PRODUCTION_METAL")


def classify(name):
    upper = (name or "").upper()
    if any(marker in upper for marker in REFERENCE_MARKERS):
        return "reference"
    if any(marker in upper for marker in METAL_MARKERS):
        return "metal"
    return "unclassified"


def audit_brep(obj_id, name, role):
    rhino_object = sc.doc.Objects.FindId(obj_id)
    brep = (
        Rhino.Geometry.Brep.TryConvertBrep(rhino_object.Geometry)
        if rhino_object else None
    )
    closed = bool(brep and brep.IsSolid)
    naked_count = None
    if brep:
        naked_curves = brep.DuplicateNakedEdgeCurves(True, True)
        naked_count = len(naked_curves) if naked_curves else 0
    return {{
        "name": name,
        "role": role,
        "closed_solid": closed,
        "naked_edge_count": naked_count,
        "geometry_passed": bool(closed and naked_count == 0),
    }}


def main():
    rows = []
    for obj_id in rs.AllObjects() or []:
        name = rs.ObjectName(obj_id) or "UNNAMED"
        role = classify(name)
        if role == "unclassified":
            continue
        rows.append(audit_brep(obj_id, name, role))

    metal_rows = [row for row in rows if row["role"] == "metal"]
    reference_rows = [row for row in rows if row["role"] == "reference"]
    blockers = []
    warnings = []

    if not metal_rows:
        blockers.append("ไม่พบชิ้นส่วนโลหะที่ตั้งชื่อตามมาตรฐาน PTR")
    failed_metal = [row["name"] for row in metal_rows if not row["geometry_passed"]]
    if failed_metal:
        blockers.append("ชิ้นส่วนโลหะไม่เป็น Closed Solid หรือมี Naked Edges: " + ", ".join(failed_metal))
    if len(metal_rows) > 1:
        blockers.append(
            "ชิ้นส่วนโลหะยังแยกกัน " + str(len(metal_rows))
            + " ชิ้น ต้องให้ช่างตรวจและรวมเป็นชิ้นงานเดียว"
        )
    if not reference_rows:
        warnings.append("ไม่พบ Stone/Guide สำหรับตรวจตำแหน่งการฝัง")
    warnings.extend([
        "ยังไม่ได้ตรวจความหนาต่ำสุดทุกตำแหน่ง",
        "ยังไม่ได้ตรวจระยะสัมผัสและความแข็งแรงของจุดเชื่อม",
        "ยังไม่ได้ตรวจ shrinkage, polishing allowance และ casting flow",
    ])

    status = "NOT_PRODUCTION_READY" if blockers else "MANUAL_REVIEW_REQUIRED"
    payload = {{
        "generator": GENERATOR,
        "status": status,
        "production_export_allowed": False,
        "metal_solid_count": len(metal_rows),
        "reference_count": len(reference_rows),
        "blockers": blockers,
        "warnings": warnings,
        "objects": rows,
    }}

    folder = os.path.dirname(OUTPUT_AUDIT)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with io.open(OUTPUT_AUDIT, "w", encoding="utf-8") as audit_file:
        json.dump(payload, audit_file, ensure_ascii=False, indent=2)

    print("PRODUCTION READINESS | status=" + status)
    print("METAL SOLIDS | count=" + str(len(metal_rows)))
    for blocker in blockers:
        print("BLOCKER | " + blocker)
    for warning in warnings:
        print("WARNING | " + warning)
    print("PRODUCTION EXPORT | BLOCKED")
    print("AUDIT JSON | " + OUTPUT_AUDIT)
    print("No geometry was modified.")


if __name__ == "__main__":
    main()
'''


def prepare_production_audit_paths(memory_root: Path) -> tuple[Path, Path]:
    """Return unique script and JSON report paths."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    script_dir = memory_root / "Rhino_Scripts"
    audit_dir = memory_root / "Production_Audits"
    script_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    return (
        script_dir / f"{stamp}_production_check.py",
        audit_dir / f"{stamp}_production_readiness.json",
    )


def save_production_readiness_script(path: Path, script: str) -> str:
    path.write_text(script, encoding="utf-8")
    return str(path)
