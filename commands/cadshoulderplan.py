"""Handler for !cadshoulderplan."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.connection_shoulder_planner import (
    build_connection_shoulder_plan_script,
    prepare_shoulder_plan_paths,
    save_connection_shoulder_plan_script,
)


async def cadshoulderplan_command(
    ctx: commands.Context, *, request: str | None = None
) -> None:
    """Attach a report-only Rhino connection and shoulder planner."""
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script_path, report_path = prepare_shoulder_plan_paths(config.memory_root)
    script = build_connection_shoulder_plan_script(report_path)
    save_connection_shoulder_plan_script(script_path, script)

    await ctx.reply(
        "🔗 สร้าง Connection Shoulder Planner แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดล v4 อยู่ ระบบจะเสนอแนวเชื่อมไหล่ซ้าย–ขวาเท่านั้น\n"
        "ไม่มีการสร้าง geometry, ไม่มี Boolean, ไม่มีการขยับหรือลบวัตถุ และไม่มี Export\n"
        f"Shoulder Plan JSON: {report_path}",
        file=discord.File(Path(script_path)),
    )
