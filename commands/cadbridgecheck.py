"""Handler for !cadbridgecheck."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.bridge_contact_validator_generator import (
    prepare_bridge_contact_validator,
    save_bridge_contact_validator,
)


async def cadbridgecheck_command(ctx: commands.Context) -> None:
    """Generate a report-only Rhino Bridge Contact Validator."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_bridge_contact_validator(memory_root)
    save_bridge_contact_validator(script_path, script)

    await ctx.reply(
        "🔎 สร้าง Bridge Contact Validator แล้ว\n"
        "ตรวจแท่งทดลองกับ Basket Support และ Ring Band รวมทั้ง Closed Solid, Naked Edge และ overlap\n"
        "รายงานอย่างเดียว ไม่แก้ ไม่ Boolean และไม่ Export โมเดล\n"
        f"Bridge Contact Report: {report_path}",
        file=discord.File(script_path),
    )
