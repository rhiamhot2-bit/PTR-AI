"""Handler for !cadupperdistances."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.upper_contact_distance_analyzer_generator import (
    prepare_upper_contact_distance_analyzer,
    save_upper_contact_distance_analyzer,
)


async def cadupperdistances_command(ctx: commands.Context) -> None:
    """Generate a report-only Rhino Upper Contact Distance Analyzer."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_upper_contact_distance_analyzer(memory_root)
    save_upper_contact_distance_analyzer(script_path, script)

    await ctx.reply(
        "📐 สร้าง Upper Contact Distance Analyzer แล้ว\n"
        "วัดระยะผิวใกล้ที่สุดของ Prongs/Supports ไปยัง Stone Seat พร้อมเวกเตอร์ X/Y/Z\n"
        "ใช้ Mesh ชั่วคราวในหน่วยความจำ ไม่เพิ่ม Mesh และไม่แก้โมเดล Rhino\n"
        f"Upper Distance Report: {report_path}",
        file=discord.File(script_path),
    )
