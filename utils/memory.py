import json
from datetime import datetime
from pathlib import Path


def save_design_memory(
    memory_root: Path,
    command: str,
    prompt: str,
    user_name: str = "unknown",
) -> str:
    folder = memory_root / "Design_History"
    folder.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M-%S_design.json")
    filepath = folder / filename

    data = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "agent": "Design",
        "command": command,
        "prompt": prompt,
        "user": user_name,
        "status": "New",
    }

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return str(filepath)
