"""Persistence for CAD validation reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def save_cad_check(memory_root: Path, report: dict[str, Any], user_name: str) -> str:
    folder = memory_root / "CAD_Checks"
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    path = folder / now.strftime("%Y-%m-%d_%H-%M-%S-%f_cadcheck.json")
    payload = {**report, "user": user_name, "created_at": now.isoformat(timespec="seconds")}
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
    return str(path)
