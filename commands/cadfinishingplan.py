"""Handler for !cadfinishingplan."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.production_finishing_plan_generator import (
    prepare_production_finishing_plan,
    save_production_finishing_plan,
)

async def cadfinishingplan_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_production_finishing_plan(root)
    save_production_finishing_plan(path, script)
    await ctx.reply(
        "📋 สร้าง Production Finishing Plan แบบ Plan Only แล้ว\n"
        "แยก KEEP / LENGTHEN_OR_REBUILD / TRIM สำหรับเตยแต่ละต้น\n"
        "พร้อมรายการตรวจรอยต่อเสาและช่องใส่พลอย โดยไม่แก้โมเดล\n"
        f"Finishing Plan: {report}",
        file=discord.File(path),
    )
