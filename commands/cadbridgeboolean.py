"""Handler for !cadbridgeboolean."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.bridge_boolean_rehearsal_generator import (
    prepare_bridge_boolean_rehearsal,
    save_bridge_boolean_rehearsal,
)


async def cadbridgeboolean_command(ctx: commands.Context) -> None:
    """Generate a copy-only Rhino Bridge Boolean Rehearsal."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_bridge_boolean_rehearsal(memory_root)
    save_bridge_boolean_rehearsal(script_path, script)

    await ctx.reply(
        "🧪 สร้าง Bridge Boolean Rehearsal แล้ว\n"
        "สคริปต์ Copy Ring Band, Basket Supports และ Bridge Trials ไปเลเยอร์ทดลองก่อน Boolean\n"
        "ต้นฉบับไม่ถูก Boolean/ลบ และ Production Export ยังถูกปิด\n"
        f"Rehearsal Report: {report_path}",
        file=discord.File(script_path),
    )
