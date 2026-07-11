import json
from datetime import datetime
from pathlib import Path


DEFAULT_STATUS = {
    "Customer_Brief": True,
    "Sketch": False,
    "CAD": False,
    "Rendering": False,
    "Quotation": False,
    "Customer_Approval": False,
    "Production": False,
    "QC": False,
    "Delivery": False,
    "Completed": False,
}


def create_project(memory_root: Path, customer_name: str, project_name: str) -> str:
    customer_name = customer_name.strip() or "Unknown"
    project_name = project_name.strip().replace(" ", "_")
    project_folder = memory_root / "Customers" / customer_name / "Projects" / project_name

    subfolders = [
        "CAD",
        "Render",
        "Images",
        "Reference",
        "Quotation",
        "Production",
        "Notes",
    ]
    for folder in subfolders:
        (project_folder / folder).mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info_file = project_folder / "project_info.txt"
    if not info_file.exists():
        info_file.write_text(
            f"Customer: {customer_name}\n"
            f"Project: {project_name}\n"
            f"Created: {now}\n"
            "Status: New\n",
            encoding="utf-8",
        )

    status_file = project_folder / "project_status.json"
    if not status_file.exists():
        status_data = {
            "customer": customer_name,
            "project": project_name,
            "created_at": now,
            "updated_at": now,
            "status": DEFAULT_STATUS.copy(),
        }
        with status_file.open("w", encoding="utf-8") as file:
            json.dump(status_data, file, ensure_ascii=False, indent=2)

    return str(project_folder)
