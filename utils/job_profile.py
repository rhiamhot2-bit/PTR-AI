"""Parameterized CAD job profiles for editable, non-Union assemblies."""
import json

PROFILE_VERSION = 1
FIELDS = {
    "prong_count": int,
    "prong_angle_deg": float,
    "prong_diameter_mm": float,
    "prong_engagement_ratio": float,
    "prong_trim_allowance_mm": float,
    "support_count": int,
    "support_style": str,
    "support_diameter_mm": float,
    "support_top_overlap_mm": float,
    "support_bottom_overlap_mm": float,
    "minimum_member_mm": float,
    "angle_tolerance_deg": float,
    "symmetry_tolerance_mm": float,
    "contact_tolerance_mm": float,
}


def parse_value(kind, value):
    return kind(value.strip())


def parse_profile_arguments(arguments):
    values = {}
    errors = []
    for token in arguments:
        if "=" not in token:
            errors.append("Expected key=value: " + token)
            continue
        key, raw = token.split("=", 1)
        key = key.strip().lower()
        if key not in FIELDS:
            errors.append("Unknown field: " + key)
            continue
        try:
            values[key] = parse_value(FIELDS[key], raw)
        except (TypeError, ValueError):
            errors.append("Invalid value for " + key)
    return values, errors


def validate_profile(profile):
    missing = [key for key in FIELDS if key not in profile]
    errors = ["Missing: " + key for key in missing]
    positive = ("prong_count", "prong_diameter_mm", "prong_trim_allowance_mm",
                "support_count", "support_diameter_mm", "minimum_member_mm",
                "angle_tolerance_deg", "symmetry_tolerance_mm", "contact_tolerance_mm")
    for key in positive:
        if key in profile and profile[key] <= 0:
            errors.append(key + " must be greater than zero")
    if "prong_angle_deg" in profile and not 0 <= profile["prong_angle_deg"] < 90:
        errors.append("prong_angle_deg must be from 0 to less than 90")
    if "prong_engagement_ratio" in profile and not 0 < profile["prong_engagement_ratio"] <= 1:
        errors.append("prong_engagement_ratio must be greater than 0 and at most 1")
    for key in ("support_top_overlap_mm", "support_bottom_overlap_mm"):
        if key in profile and profile[key] < 0:
            errors.append(key + " must not be negative")
    if profile.get("support_style", "").upper() not in ("STRAIGHT", "CURVED", "CUSTOM"):
        errors.append("support_style must be STRAIGHT, CURVED, or CUSTOM")
    return errors


def normalized_profile(profile):
    result = {"profile_version": PROFILE_VERSION, "assembly_mode": "EDITABLE_NON_UNION"}
    result.update({key: profile[key] for key in FIELDS if key in profile})
    if "support_style" in result:
        result["support_style"] = result["support_style"].upper()
    return result


def save_profile(path, profile):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(normalized_profile(profile), ensure_ascii=False, indent=2), encoding="utf-8")


def load_profile(path):
    return json.loads(path.read_text(encoding="utf-8"))
