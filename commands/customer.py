import shlex

from discord.ext import commands

from utils.customer_memory import create_or_update_customer


def parse_customer_text(text: str) -> dict[str, str]:
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

    try:
        parts = shlex.split(text)
    except ValueError:
        parts = text.split()

    if not parts:
        return data

    data["customer_name"] = parts[0]
    field_map = {
        "country": "country",
        "phone": "phone",
        "email": "email",
        "budget": "budget",
        "stone": "favorite_stone",
        "metal": "favorite_metal",
        "notes": "notes",
    }

    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        destination = field_map.get(key.lower().strip())
        if destination:
            data[destination] = value.strip()

    return data


async def customer_command(
    ctx: commands.Context,
    *,
    customer: str | None = None,
) -> None:
    if not customer:
        await ctx.send(
            "Usage:\n"
            '!customer Ahmed country=UAE budget=500000 '
            'stone=Emerald metal=22K notes="Royal ring customer"'
        )
        return

    data = parse_customer_text(customer)
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    file_path = create_or_update_customer(
        memory_root=config.memory_root,
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
        f"Saved : {file_path}"
    )
