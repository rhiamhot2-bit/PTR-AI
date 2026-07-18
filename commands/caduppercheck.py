"""Handler for !caduppercheck."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.upper_setting_contact_validator_generator import (
    prepare_upper_setting_contact_validator,
    save_upper_setting_contact_validator,
)


async def caduppercheck_command(ctx: commands.Context) -> None:
    """Generate a report-only Rhino Upper Setting Contact Validator."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_upper_setting_contact_validator(memory_root)
    save_upper_setting_contact_validator(script_path, script)

    await ctx.reply(
        "💍 สร้าง Upper Setting Contact Validator แล้ว\n"
        "ตรวจ Stone Seat กับ Prongs 4 ต้นและ Basket Supports 2 ต้น รวม 6 คู่\n"
        "วัดผิวตัด ปริมาตรซ้อน และความลึกขั้นต่ำ โดยไม่เพิ่ม Boolean geometry ลงโมเดล\n"
        f"Upper Contact Report: {report_path}",
        file=discord.File(script_path),
    )
