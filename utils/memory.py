import json
from datetime import datetime
from pathlib import Path


MEMORY_ROOT = Path(r"C:\Users\rhoam\Desktop\PTR_AI_COMPANY\Memory")


def save_design_memory(command: str, prompt: str, user_name: str = "unknown") -> str:
    folder = MEMORY_ROOT / "Design_History"
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
        "status": "New"
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(filepath)