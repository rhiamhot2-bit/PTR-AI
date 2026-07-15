"""Handler for !cadbooleantrial."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.safe_boolean_trial_generator import (
    build_safe_boolean_trial_script,
    prepare_safe_boolean_trial_paths,
    save_safe_boolean_trial_script,
)


async def cadbooleantrial_command(
    ctx: commands.Context, *, request: str | None = None
) -> None:
    """Attach a staged, non-destructive Rhino Boolean trial."""
    config = ctx.bot.ptr_config
    script_path, audit_path = prepare_safe_boolean_trial_paths(config.memory_root)
    script = build_safe_boolean_trial_script(audit_path)
    save_safe_boolean_trial_script(script_path, script)

    await ctx.reply(
        "🧪 สร้าง Safe Boolean Trial แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดลล่าสุดอยู่ ระบบจะทดลอง Boolean แบบแบ่ง Stage "
        "บนสำเนาใน Layer PTR_BOOLEAN_TRIAL เท่านั้น\n"
        "ต้นฉบับไม่ถูกลบ/ย้าย/เปลี่ยนชื่อ, ไม่รวมพลอยหรือ Guide และไม่ Export งานผลิต\n"
        f"Boolean Trial JSON: {audit_path}",
        file=discord.File(Path(script_path)),
    )
