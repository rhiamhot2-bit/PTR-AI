import json
from datetime import datetime
from pathlib import Path


MEMORY_ROOT = Path(r"C:\Users\rhoam\Desktop\PTR_AI_COMPANY\Memory")
CUSTOMERS_ROOT = MEMORY_ROOT / "Customers"


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


def create_project(customer_name: str, project_name: str) -> str:
    customer_name = customer_name.strip()
    project_name = project_name.strip().replace(" ", "_")

    customer_folder = CUSTOMERS_ROOT / customer_name
    project_folder = customer_folder / "Projects" / project_name

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

    info_file = project_folder / "project_info.txt"

    if not info_file.exists():
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"Customer: {customer_name}\n")
            f.write(f"Project: {project_name}\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Status: New\n")

    status_file = project_folder / "project_status.json"

    if not status_file.exists():
        status_data = {
            "customer": customer_name,
            "project": project_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": DEFAULT_STATUS,
        }

        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)

    return str(project_folder)