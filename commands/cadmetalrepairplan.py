"""Handler for !cadmetalrepairplan."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.metal_gap_repair_planner_generator import (
    prepare_metal_gap_repair_planner,
    save_metal_gap_repair_planner,
)


async def cadmetalrepairplan_command(ctx: commands.Context) -> None:
    """Generate a report-only Rhino metal gap repair plan."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_metal_gap_repair_planner(memory_root)
    save_metal_gap_repair_planner(script_path, script)

    await ctx.reply(
        "🧭 สร้าง Metal Gap Repair Planner แล้ว\n"
        "สคริปต์จะเสนอคู่โลหะ ระยะ แกน ทิศทาง และระยะต่อพร้อม safe overlap\n"
        "เป็นแผนตรวจสอบเท่านั้น ไม่ขยับ ไม่ยืด ไม่ Boolean และไม่ Export โมเดล\n"
        f"Repair Plan JSON: {report_path}",
        file=discord.File(script_path),
    )
