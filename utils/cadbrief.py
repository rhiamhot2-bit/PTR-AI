"""Parse jewelry requests into a structured CAD brief."""

from __future__ import annotations

import re
from typing import Any


JEWELRY_TYPES = {
    "ring": ("แหวน", "ring"),
    "pendant": ("จี้", "pendant"),
    "earrings": ("ต่างหู", "earring", "earrings"),
    "bracelet": ("สร้อยข้อมือ", "กำไล", "bracelet", "bangle"),
    "necklace": ("สร้อยคอ", "necklace"),
}

STONE_TYPES = {
    "emerald": ("มรกต", "emerald"),
    "diamond": ("เพชร", "diamond"),
    "ruby": ("ทับทิม", "ruby"),
    "sapphire": ("ไพลิน", "sapphire"),
    "tourmaline": ("ทัวร์มาลีน", "tourmaline"),
    "pearl": ("มุก", "pearl"),
}

STONE_SHAPES = {
    "oval": ("oval", "โอวัล", "วงรี"),
    "round": ("round", "กลม"),
    "pear": ("pear", "หยดน้ำ"),
    "marquise": ("marquise", "มาคี", "มาร์คี"),
    "emerald_cut": ("emerald cut", "เอเมอรัลด์คัต"),
    "cushion": ("cushion", "คุชชั่น"),
    "princess": ("princess", "ปริ๊นเซส"),
    "heart": ("heart", "หัวใจ"),
}


def _find_alias(text: str, aliases: dict[str, tuple[str, ...]]) -> str | None:
    lowered = text.lower()
    for normalized, values in aliases.items():
        if any(value.lower() in lowered for value in values):
            return normalized
    return None


def _find_number(pattern: str, text: str) -> float | None:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return float(match.group(1)) if match else None


def _clean_number(value: float | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if value.is_integer() else value


def parse_cad_brief(prompt: str) -> dict[str, Any]:
    """Extract practical CAD fields from Thai or English jewelry text."""
    normalized = prompt.replace("×", "x")
    jewelry_type = _find_alias(normalized, JEWELRY_TYPES)
    stone_type = _find_alias(normalized, STONE_TYPES)
    stone_shape = _find_alias(normalized, STONE_SHAPES)

    ring_size = _find_number(
        r"(?:ไซซ์|size|ring\s*size)\s*[:=]?\s*(\d+(?:\.\d+)?)",
        normalized,
    )
    dimensions_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\s*(?:มม\.?|mm)?",
        normalized,
        flags=re.IGNORECASE,
    )
    length_mm = float(dimensions_match.group(1)) if dimensions_match else None
    width_mm = float(dimensions_match.group(2)) if dimensions_match else None

    metal_match = re.search(
        r"(?:ทอง\s*)?(9|10|14|18|22|24)\s*[kK]",
        normalized,
        flags=re.IGNORECASE,
    )
    metal = f"{metal_match.group(1)}K gold" if metal_match else None
    if "platinum" in normalized.lower() or "แพลทินัม" in normalized:
        metal = "platinum"
    elif "silver" in normalized.lower() or "เงิน" in normalized:
        metal = "silver"

    prong_count = _find_number(
        r"(\d+)\s*(?:เตย|prongs?|claws?)",
        normalized,
    )
    setting = None
    lowered = normalized.lower()
    if prong_count is not None or "หนามเตย" in normalized or "prong" in lowered:
        setting = "prong"
    elif "หุ้ม" in normalized or "bezel" in lowered:
        setting = "bezel"
    elif "pavé" in lowered or "pave" in lowered or "พาเว่" in normalized:
        setting = "pave"
    elif "halo" in lowered or "ล้อม" in normalized:
        setting = "halo"

    missing_fields: list[str] = []
    required = {
        "ประเภทเครื่องประดับ": jewelry_type,
        "ชนิดโลหะ": metal,
        "ชนิดพลอยกลาง": stone_type,
        "รูปทรงพลอย": stone_shape,
        "ขนาดพลอย": dimensions_match,
        "รูปแบบการฝัง": setting,
    }
    if jewelry_type == "ring":
        required["ไซซ์แหวน"] = ring_size
    for label, value in required.items():
        if value is None:
            missing_fields.append(label)

    return {
        "jewelry_type": jewelry_type,
        "ring_size": _clean_number(ring_size),
        "metal": metal,
        "center_stone": {
            "type": stone_type,
            "shape": stone_shape,
            "length_mm": _clean_number(length_mm),
            "width_mm": _clean_number(width_mm),
        },
        "setting": {
            "type": setting,
            "prong_count": _clean_number(prong_count),
        },
        "status": "ready_for_cad" if not missing_fields else "needs_information",
        "missing_fields": missing_fields,
        "original_prompt": prompt.strip(),
    }


def format_cad_brief(brief: dict[str, Any]) -> str:
    """Format a CAD brief for a concise Discord response."""
    stone = brief["center_stone"]
    setting = brief["setting"]
    dimensions = "ไม่ระบุ"
    if stone["length_mm"] is not None and stone["width_mm"] is not None:
        dimensions = f'{stone["length_mm"]} x {stone["width_mm"]} มม.'

    status = "✅ พร้อมทำ CAD" if brief["status"] == "ready_for_cad" else "🟡 ต้องถามข้อมูลเพิ่ม"
    missing = ", ".join(brief["missing_fields"]) if brief["missing_fields"] else "ไม่มี"

    return (
        "**CAD BRIEF – PTR JEW3D**\n"
        f"ประเภทงาน: {brief['jewelry_type'] or 'ไม่ระบุ'}\n"
        f"ไซซ์แหวน: {brief['ring_size'] if brief['ring_size'] is not None else 'ไม่ระบุ'}\n"
        f"โลหะ: {brief['metal'] or 'ไม่ระบุ'}\n"
        f"พลอยกลาง: {stone['type'] or 'ไม่ระบุ'}\n"
        f"รูปทรง: {stone['shape'] or 'ไม่ระบุ'}\n"
        f"ขนาดพลอย: {dimensions}\n"
        f"รูปแบบฝัง: {setting['type'] or 'ไม่ระบุ'}\n"
        f"จำนวนหนามเตย: {setting['prong_count'] if setting['prong_count'] is not None else 'ไม่ระบุ'}\n"
        f"สถานะ: {status}\n"
        f"ข้อมูลที่ยังขาด: {missing}"
    )
