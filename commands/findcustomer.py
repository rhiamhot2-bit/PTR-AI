import json

from discord.ext import commands


async def findcustomer_command(
    ctx: commands.Context,
    *,
    customer: str | None = None,
) -> None:
    if not customer:
        await ctx.send("Usage: !findcustomer <name>")
        return

    customer_name = customer.strip()
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    customer_file = config.memory_root / "Customers" / customer_name / "customer.json"

    if not customer_file.exists():
        await ctx.send(f"❌ ไม่พบข้อมูลลูกค้า: {customer_name}")
        return

    with customer_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    await ctx.send(
        f"👤 Customer Profile\n\n"
        f"Name : {data.get('customer', '')}\n"
        f"Country : {data.get('country', '')}\n"
        f"Phone : {data.get('phone', '')}\n"
        f"Email : {data.get('email', '')}\n"
        f"Budget : {data.get('budget', '')}\n"
        f"Stone : {data.get('favorite_stone', '')}\n"
        f"Metal : {data.get('favorite_metal', '')}\n"
        f"Notes : {data.get('notes', '')}\n"
        f"Updated : {data.get('updated_at', '')}"
    )
