from discord.ext import commands

from utils.customer_memory import create_or_update_customer


def parse_customer_text(text: str) -> dict:
    data = {
        "customer_name": "",
        "country": "",
        "phone": "",
        "email": "",
        "budget": "",
        "favorite_stone": "",
        "favorite_metal": "",
        "notes": "",
    }

    parts = text.split()

    if not parts:
        return data

    data["customer_name"] = parts[0]

    for part in parts[1:]:
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.lower().strip()
        value = value.strip().replace('"', "")

        if key == "country":
            data["country"] = value
        elif key == "phone":
            data["phone"] = value
        elif key == "email":
            data["email"] = value
        elif key == "budget":
            data["budget"] = value
        elif key == "stone":
            data["favorite_stone"] = value
        elif key == "metal":
            data["favorite_metal"] = value
        elif key == "notes":
            data["notes"] = value

    return data


async def customer_command(
    ctx: commands.Context,
    *,
    customer: str | None = None,
):
    if not customer:
        await ctx.send(
            "Usage:\n"
            "!customer Ahmed country=UAE budget=500000 stone=Emerald metal=22K"
        )
        return

    data = parse_customer_text(customer)

    file = create_or_update_customer(
        customer_name=data["customer_name"],
        country=data["country"],
        phone=data["phone"],
        email=data["email"],
        budget=data["budget"],
        favorite_stone=data["favorite_stone"],
        favorite_metal=data["favorite_metal"],
        notes=data["notes"],
    )

    await ctx.send(
        f"✅ Customer Updated\n\n"
        f"Name : {data['customer_name']}\n"
        f"Country : {data['country']}\n"
        f"Budget : {data['budget']}\n"
        f"Stone : {data['favorite_stone']}\n"
        f"Metal : {data['favorite_metal']}\n"
        f"Saved : {file}"
    )