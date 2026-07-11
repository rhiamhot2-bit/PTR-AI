import json
from datetime import datetime
from pathlib import Path


def create_or_update_customer(
    memory_root: Path,
    customer_name: str,
    country: str = "",
    phone: str = "",
    email: str = "",
    budget: str = "",
    favorite_stone: str = "",
    favorite_metal: str = "",
    notes: str = "",
) -> str:
    customer_name = customer_name.strip() or "Unknown"
    customer_folder = memory_root / "Customers" / customer_name
    customer_folder.mkdir(parents=True, exist_ok=True)
    customer_file = customer_folder / "customer.json"

    if customer_file.exists():
        with customer_file.open("r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {
            "customer": customer_name,
            "country": "",
            "phone": "",
            "email": "",
            "budget": "",
            "favorite_stone": "",
            "favorite_metal": "",
            "projects": [],
            "cad_files": [],
            "quotations": [],
            "notes": "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": "",
        }

    updates = {
        "country": country,
        "phone": phone,
        "email": email,
        "budget": budget,
        "favorite_stone": favorite_stone,
        "favorite_metal": favorite_metal,
        "notes": notes,
    }
    for key, value in updates.items():
        if value:
            data[key] = value

    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with customer_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return str(customer_file)
