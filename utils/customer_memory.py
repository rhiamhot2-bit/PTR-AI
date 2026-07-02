import json
from datetime import datetime
from pathlib import Path


MEMORY_ROOT = Path(r"C:\Users\rhoam\Desktop\PTR_AI_COMPANY\Memory")
CUSTOMERS_ROOT = MEMORY_ROOT / "Customers"


def create_or_update_customer(
    customer_name: str,
    country: str = "",
    phone: str = "",
    email: str = "",
    budget: str = "",
    favorite_stone: str = "",
    favorite_metal: str = "",
    notes: str = "",
) -> str:
    customer_name = customer_name.strip()

    if not customer_name:
        customer_name = "Unknown"

    customer_folder = CUSTOMERS_ROOT / customer_name
    customer_folder.mkdir(parents=True, exist_ok=True)

    customer_file = customer_folder / "customer.json"

    if customer_file.exists():
        with open(customer_file, "r", encoding="utf-8") as f:
            data = json.load(f)
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
            "updated_at": ""
        }

    if country:
        data["country"] = country
    if phone:
        data["phone"] = phone
    if email:
        data["email"] = email
    if budget:
        data["budget"] = budget
    if favorite_stone:
        data["favorite_stone"] = favorite_stone
    if favorite_metal:
        data["favorite_metal"] = favorite_metal
    if notes:
        data["notes"] = notes

    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(customer_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(customer_file)