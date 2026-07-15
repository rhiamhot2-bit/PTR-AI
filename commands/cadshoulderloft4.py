"""Handler for !cadshoulderloft4."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.shoulder_loft_v4_generator import (
    build_shoulder_loft_v4_script,
    prepare_shoulder_loft_v4_paths,
    save_shoulder_loft_v4_script,
)


async def cadshoulderloft4_command(
    ctx: commands.Context, *, request: str | None = None
) -> None:
    """Generate a Rhino report script that verifies shoulder contact."""

    config = ctx.bot.ptr_config
    script_path, report_path = prepare_shoulder_loft_v4_paths(config.memory_root)
    script = build_shoulder_loft_v4_script(report_path)
    save_shoulder_loft_v4_script(script, script_path)

    await ctx.reply(
        "🔎 สร้าง Shoulder Loft v4 Contact Audit แล้ว\n"
        "เปิดโมเดล v4 ใน Rhino แล้วรันไฟล์นี้ เพื่อตรวจการชนจริงระหว่าง "
        "Shoulder ↔ ก้านแหวน และ Shoulder ↔ ชุดกะเปาะ\n"
        "สคริปต์นี้ตรวจและรายงานเท่านั้น: ไม่มี Boolean, ไม่ลบวัตถุ และไม่ Export งานผลิต\n"
        f"Contact Audit JSON: {report_path}",
        file=discord.File(Path(script_path)),
    )
