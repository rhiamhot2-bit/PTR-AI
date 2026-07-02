import json
from pathlib import Path

from discord.ext import commands


CUSTOMERS_ROOT = Path(r"C:\Users\rhoam\Desktop\PTR_AI_COMPANY\Memory\Customers")


async def findcustomer_command(
    ctx: commands.Context,
    *,
    customer: str | None = None,
):
    if not customer:
        await ctx.send("Usage: !findcustomer <name>")
        return

    customer_name = customer.strip()
    customer_file = CUSTOMERS_ROOT / customer_name / "customer.json"

    if not customer_file.exists():
        await ctx.send(f"❌ ไม่พบข้อมูลลูกค้า: {customer_name}")
        return

    with open(customer_file, "r", encoding="utf-8") as f:
        data = json.load(f)

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