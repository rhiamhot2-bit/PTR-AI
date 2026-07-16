from pathlib import Path

import discord
from discord.ext import commands

from config import settings
from utils.shoulder_contact_validator import (
    prepare_shoulder_contact_validator,
    save_shoulder_contact_validator,
)


async def cadshouldercheck_command(ctx: commands.Context) -> None:
    memory_root = Path(settings.memory_root)
    script_path, report_path, script = prepare_shoulder_contact_validator(memory_root)
    save_shoulder_contact_validator(script_path, script)

    message = (
        "🔍 สร้าง Shoulder Contact Validator แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดล v4 และมี Shoulder Loft อยู่ ระบบจะตรวจการแตะก้านแหวน "
        "การแตะฐานกระเปาะ และความสมมาตรซ้าย–ขวา\n"
        "เป็นรายงานเท่านั้น ไม่มีการสร้าง geometry, Boolean, ลบ, ย้าย หรือ Export\n"
        "Production Export จะถูกบล็อกไว้จนกว่าผลตรวจและช่างจิวเวลรี่จะยืนยัน\n"
        f"Shoulder Contact JSON: {report_path}"
    )
    await ctx.reply(message, file=discord.File(script_path))
