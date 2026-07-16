"""Handler for !cadmetalcheck."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.metal_union_readiness_generator import (
    prepare_metal_union_validator,
    save_metal_union_validator,
)


async def cadmetalcheck_command(ctx: commands.Context) -> None:
    """Generate a report-only Rhino metal-union readiness validator."""
    config = ctx.bot.ptr_config
    memory_root = Path(config.memory_root)

    script_path, report_path, script = prepare_metal_union_validator(memory_root)
    save_metal_union_validator(script_path, script)

    message = (
        "🧩 สร้าง Metal Union Readiness Validator แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดล v4 และมี Shoulder Loft อยู่ ระบบจะตรวจ closed solid, "
        "naked edges และเครือข่ายการสัมผัสของชิ้นส่วนโลหะ\n"
        "เป็นรายงานเท่านั้น ไม่มีการ Boolean, ลบ, ย้าย, เปลี่ยนชื่อ หรือ Export\n"
        "ผลผ่านเบื้องต้นยังต้องให้ช่างจิวเวลรี่ตรวจ intersection และยืนยันก่อนรวมชิ้นงาน/"
        "Production Export\n"
        f"Metal Union Audit JSON: {report_path}"
    )
    await ctx.reply(message, file=discord.File(script_path))
