"""Handler for !cadmetalgaps."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.metal_contact_gap_analyzer_generator import (
    prepare_metal_contact_gap_analyzer,
    save_metal_contact_gap_analyzer,
)


async def cadmetalgaps_command(ctx: commands.Context) -> None:
    """Generate a report-only Rhino metal contact-gap analyzer."""
    config = ctx.bot.ptr_config
    memory_root = Path(config.memory_root)

    script_path, report_path, script = prepare_metal_contact_gap_analyzer(memory_root)
    save_metal_contact_gap_analyzer(script_path, script)

    message = (
        "📏 สร้าง Metal Contact Gap Analyzer แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดลซึ่งผ่าน Metal Union Rehearsal ระบบจะตรวจโลหะเป็นคู่ "
        "และรายงาน INTERSECTING, CONTACT_CANDIDATE, SMALL_GAP หรือ OPEN_GAP\n"
        "ค่าระยะเป็นค่าประเมินจาก Bounding Box สำหรับคัดกรอง ต้องตรวจผิวจริงใน Rhino อีกครั้ง\n"
        "คำสั่งนี้ไม่ Copy, Boolean, ลบ, ย้าย, เปลี่ยนชื่อ หรือ Export ชิ้นงาน\n"
        f"Contact Gap Audit JSON: {report_path}"
    )
    await ctx.reply(message, file=discord.File(script_path))
