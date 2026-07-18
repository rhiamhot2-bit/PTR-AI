"""Handler for !cadsupportcurveboolean."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.curved_support_boolean_rehearsal_generator import (
    prepare_curved_support_boolean_rehearsal,
    save_curved_support_boolean_rehearsal,
)

async def cadsupportcurveboolean_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_curved_support_boolean_rehearsal(root)
    save_curved_support_boolean_rehearsal(path,script)
    await ctx.reply(
        "🧪 สร้าง Curved Support Boolean Rehearsal แล้ว\n"
        "Union เฉพาะ Duplicate Brep ของ Stone Seat, Ring Band และ Curved Supports 2 ข้าง\n"
        "ต้นฉบับไม่ถูกแก้หรือลบ และ Production Export ยังถูก Block\n"
        f"Rehearsal Report: {report}",
        file=discord.File(path),
    )
