"""Persistence helpers for structured CAD briefs."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def save_cad_brief(
    memory_root: Path,
    brief: dict[str, Any],
    user_name: str,
) -> str:
    """Save a CAD brief as UTF-8 JSON and return its path."""
    folder = memory_root / "CAD_Briefs"
    folder.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filepath = folder / now.strftime("%Y-%m-%d_%H-%M-%S-%f_cadbrief.json")
    payload = {
        **brief,
        "user": user_name,
        "created_at": now.isoformat(timespec="seconds"),
    }
    with filepath.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return str(filepath)
