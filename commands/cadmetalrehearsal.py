"""Handler for !cadmetalrehearsal."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.metal_union_rehearsal_generator import (
    prepare_metal_union_rehearsal,
    save_metal_union_rehearsal,
)


async def cadmetalrehearsal_command(ctx: commands.Context) -> None:
    """Generate a copy-only Rhino metal-union rehearsal."""
    config = ctx.bot.ptr_config
    memory_root = Path(config.memory_root)

    script_path, report_path, script = prepare_metal_union_rehearsal(memory_root)
    save_metal_union_rehearsal(script_path, script)

    message = (
        "🧪 สร้าง Metal Union Rehearsal แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดล v4 และมี Shoulder Loft อยู่ ระบบจะคัดลอกเฉพาะ"
        "ชิ้นส่วนโลหะ และทดลอง BooleanUnion เฉพาะสำเนา\n"
        "พลอย, Girdle Guides, Guides และ Notes จะไม่ถูกนำไปรวม\n"
        "ต้นฉบับไม่ถูกแก้ไข ไม่มีการลบ และไม่มี Production Export\n"
        "ผลผ่านยังต้องให้ช่างจิวเวลรี่ตรวจรอยต่อก่อนใช้ผลิต\n"
        f"Rehearsal Audit JSON: {report_path}"
    )
    await ctx.reply(message, file=discord.File(script_path))
