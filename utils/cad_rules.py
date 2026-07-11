"""Rule-based readiness checks before generating Rhino jewelry scripts."""

from __future__ import annotations

import re
from typing import Any

from utils.cadbrief import parse_cad_brief


RULESET_VERSION = "ptr-ring-v1"

RULES = {
    "shank_width_mm": {"fail_below": 1.8, "warn_below": 2.2},
    "shank_thickness_mm": {"fail_below": 1.5, "warn_below": 1.8},
    "prong_diameter_mm": {"fail_below": 0.6, "warn_below": 0.7},
    "seat_clearance_mm": {"pass_min": 0.05, "pass_max": 0.15, "fail_max": 0.25},
    "head_height_mm": {"warn_above": 7.0},
}


def _extract(patterns: tuple[str, ...], text: str) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def extract_engineering_values(prompt: str) -> dict[str, float | None]:
    """Extract explicit engineering dimensions from Thai or English text."""
    return {
        "shank_width_mm": _extract(
            (
                r"(?:ก้าน(?:แหวน)?\s*กว้าง|shank\s*width)\s*[:=]?\s*(\d+(?:\.\d+)?)",
                r"(?:ความกว้างก้าน)\s*[:=]?\s*(\d+(?:\.\d+)?)",
            ),
            prompt,
        ),
        "shank_thickness_mm": _extract(
            (
                r"(?:ก้าน(?:แหวน)?\s*หนา|shank\s*thickness)\s*[:=]?\s*(\d+(?:\.\d+)?)",
                r"(?:ความหนาก้าน)\s*[:=]?\s*(\d+(?:\.\d+)?)",
            ),
            prompt,
        ),
        "prong_diameter_mm": _extract(
            (
                r"(?:หนามเตย(?:\s*(?:หนา|เส้นผ่านศูนย์กลาง))?|prong\s*diameter)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:มม\.?|mm)",
            ),
            prompt,
        ),
        "seat_clearance_mm": _extract(
            (
                r"(?:ระยะเผื่อฝัง|seat\s*clearance|clearance)\s*[:=]?\s*(\d+(?:\.\d+)?)",
            ),
            prompt,
        ),
        "head_height_mm": _extract(
            (
                r"(?:หัวแหวนสูง|ความสูงหัวแหวน|head\s*height)\s*[:=]?\s*(\d+(?:\.\d+)?)",
            ),
            prompt,
        ),
    }


def _minimum_check(
    field: str,
    label: str,
    value: float | None,
    fail_below: float,
    warn_below: float,
) -> dict[str, Any]:
    if value is None:
        return {
            "field": field,
            "label": label,
            "status": "missing",
            "value_mm": None,
            "message": "ยังไม่ระบุค่า",
        }
    if value < fail_below:
        status, message = "fail", f"ต่ำกว่าค่าต่ำสุด {fail_below:g} มม."
    elif value < warn_below:
        status, message = "warning", f"ผ่านขั้นต่ำ แต่แนะนำอย่างน้อย {warn_below:g} มม."
    else:
        status, message = "pass", "ผ่านค่าตั้งต้น"
    return {
        "field": field,
        "label": label,
        "status": status,
        "value_mm": value,
        "message": message,
    }


def validate_cad_request(prompt: str) -> dict[str, Any]:
    """Build a CAD brief and validate explicit ring engineering dimensions."""
    brief = parse_cad_brief(prompt)
    values = extract_engineering_values(prompt)
    checks = [
        _minimum_check(
            "shank_width_mm",
            "ความกว้างก้านแหวน",
            values["shank_width_mm"],
            RULES["shank_width_mm"]["fail_below"],
            RULES["shank_width_mm"]["warn_below"],
        ),
        _minimum_check(
            "shank_thickness_mm",
            "ความหนาก้านแหวน",
            values["shank_thickness_mm"],
            RULES["shank_thickness_mm"]["fail_below"],
            RULES["shank_thickness_mm"]["warn_below"],
        ),
        _minimum_check(
            "prong_diameter_mm",
            "ขนาดหนามเตย",
            values["prong_diameter_mm"],
            RULES["prong_diameter_mm"]["fail_below"],
            RULES["prong_diameter_mm"]["warn_below"],
        ),
    ]

    clearance = values["seat_clearance_mm"]
    if clearance is None:
        clearance_check = {
            "field": "seat_clearance_mm",
            "label": "ระยะเผื่อฝัง",
            "status": "missing",
            "value_mm": None,
            "message": "ยังไม่ระบุค่า",
        }
    elif clearance <= 0 or clearance > RULES["seat_clearance_mm"]["fail_max"]:
        clearance_check = {
            "field": "seat_clearance_mm",
            "label": "ระยะเผื่อฝัง",
            "status": "fail",
            "value_mm": clearance,
            "message": "อยู่นอกช่วงตรวจสอบ 0–0.25 มม.",
        }
    elif not (
        RULES["seat_clearance_mm"]["pass_min"]
        <= clearance
        <= RULES["seat_clearance_mm"]["pass_max"]
    ):
        clearance_check = {
            "field": "seat_clearance_mm",
            "label": "ระยะเผื่อฝัง",
            "status": "warning",
            "value_mm": clearance,
            "message": "แนะนำช่วง 0.05–0.15 มม.",
        }
    else:
        clearance_check = {
            "field": "seat_clearance_mm",
            "label": "ระยะเผื่อฝัง",
            "status": "pass",
            "value_mm": clearance,
            "message": "ผ่านค่าตั้งต้น",
        }
    checks.append(clearance_check)

    height = values["head_height_mm"]
    if height is None:
        height_check = {
            "field": "head_height_mm",
            "label": "ความสูงหัวแหวน",
            "status": "missing",
            "value_mm": None,
            "message": "ยังไม่ระบุค่า",
        }
    elif height > RULES["head_height_mm"]["warn_above"]:
        height_check = {
            "field": "head_height_mm",
            "label": "ความสูงหัวแหวน",
            "status": "warning",
            "value_mm": height,
            "message": "สูงกว่า 7 มม. ควรตรวจการเกี่ยวเสื้อผ้าและความสบาย",
        }
    else:
        height_check = {
            "field": "head_height_mm",
            "label": "ความสูงหัวแหวน",
            "status": "pass",
            "value_mm": height,
            "message": "ผ่านค่าตั้งต้น",
        }
    checks.append(height_check)

    statuses = {check["status"] for check in checks}
    if "fail" in statuses:
        overall = "blocked"
    elif "missing" in statuses:
        overall = "needs_information"
    elif "warning" in statuses:
        overall = "review_required"
    else:
        overall = "ready_for_rhino"

    return {
        "ruleset_version": RULESET_VERSION,
        "brief": brief,
        "engineering_values": values,
        "checks": checks,
        "overall_status": overall,
        "professional_review_required": True,
    }


def format_validation_report(report: dict[str, Any]) -> str:
    """Create a concise Thai Discord report."""
    icons = {"pass": "✅", "warning": "⚠️", "fail": "❌", "missing": "⬜"}
    overall_labels = {
        "ready_for_rhino": "✅ พร้อมให้ช่างตรวจขั้นสุดท้ายก่อนสร้าง Rhino Script",
        "review_required": "⚠️ ต้องให้ช่างตรวจคำเตือนก่อนสร้าง Rhino Script",
        "needs_information": "🟡 ต้องเพิ่มข้อมูลก่อนสร้าง Rhino Script",
        "blocked": "❌ ไม่ผ่าน ห้ามสร้าง Rhino Script",
    }
    lines = ["**CAD RULES CHECK – PTR JEW3D**"]
    for check in report["checks"]:
        value = (
            f'{check["value_mm"]:g} มม.'
            if check["value_mm"] is not None
            else "ไม่ระบุ"
        )
        lines.append(
            f'{icons[check["status"]]} {check["label"]}: {value} — {check["message"]}'
        )
    lines.extend(
        (
            f'สถานะรวม: {overall_labels[report["overall_status"]]}',
            f'Ruleset: {report["ruleset_version"]}',
            "หมายเหตุ: ค่ารุ่นแรกเป็นค่าเริ่มต้น ต้องให้ช่างจิวเวลรี่ยืนยันก่อนผลิตจริง",
        )
    )
    return "\n".join(lines)
