import json
from pathlib import Path
from datetime import datetime


MEMORY_ROOT = Path(r"C:\Users\rhoam\Desktop\PTR_AI_COMPANY\Memory")
CUSTOMERS_ROOT = MEMORY_ROOT / "Customers"


WORKFLOW = [
    "Customer_Brief",
    "Sketch",
    "CAD",
    "Rendering",
    "Quotation",
    "Customer_Approval",
    "Production",
    "QC",
    "Delivery",
    "Completed",
]


def get_status_file(customer: str, project: str) -> Path:
    customer = customer.strip()
    project = project.strip().replace(" ", "_")

    return (
        CUSTOMERS_ROOT
        / customer
        / "Projects"
        / project
        / "project_status.json"
    )


def load_status(customer: str, project: str):
    file = get_status_file(customer, project)

    if not file.exists():
        return None

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_status(customer: str, project: str, data: dict) -> None:
    file = get_status_file(customer, project)

    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_workflow(customer: str, project: str) -> dict:
    data = load_status(customer, project)

    if data is None:
        return {
            "success": False,
            "message": "ไม่พบ project_status.json",
            "current_step": "",
            "next_step": "",
        }

    status = data.get("status", {})

    for step in WORKFLOW:
        if not status.get(step, False):
            status[step] = True
            data["status"] = status
            save_status(customer, project, data)

            return {
                "success": True,
                "message": "Workflow updated",
                "current_step": step,
                "next_step": get_next_step(step),
            }

    return {
        "success": True,
        "message": "Project already completed",
        "current_step": "Completed",
        "next_step": "",
    }


def get_next_step(current_step: str) -> str:
    if current_step not in WORKFLOW:
        return ""

    index = WORKFLOW.index(current_step)

    if index + 1 >= len(WORKFLOW):
        return ""

    return WORKFLOW[index + 1]


def get_project_status(customer: str, project: str) -> dict:
    data = load_status(customer, project)

    if data is None:
        return {
            "success": False,
            "message": "ไม่พบ project_status.json",
            "status_text": "",
        }

    status = data.get("status", {})

    lines = []
    lines.append("📋 Project Status")
    lines.append("")
    lines.append(f"Customer : {data.get('customer', customer)}")
    lines.append(f"Project : {data.get('project', project)}")
    lines.append("")
    
    for step in WORKFLOW:
        icon = "✅" if status.get(step, False) else "⬜"
        lines.append(f"{icon} {step}")

    lines.append("")
    lines.append(f"Updated : {data.get('updated_at', '')}")

    return {
        "success": True,
        "message": "Status loaded",
        "status_text": "\n".join(lines),
    }


def get_progress(customer: str, project: str) -> dict:
    data = load_status(customer, project)

    if data is None:
        return {
            "success": False,
            "message": "ไม่พบ project_status.json",
            "percent": 0,
        }

    status = data.get("status", {})
    total = len(WORKFLOW)
    done = 0

    for step in WORKFLOW:
        if status.get(step, False):
            done += 1

    percent = int((done / total) * 100)

    return {
        "success": True,
        "message": "Progress calculated",
        "done": done,
        "total": total,
        "percent": percent,
    }