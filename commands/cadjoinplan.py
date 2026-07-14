"""Handler for !cadjoinplan."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.geometry_join_planner import (
    build_geometry_join_plan_script,
    prepare_join_plan_paths,
    save_geometry_join_plan_script,
)


async def cadjoinplan_command(
    ctx: commands.Context, *, request: str | None = None
) -> None:
    """Attach a report-only Rhino geometry join planner."""
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script_path, report_path = prepare_join_plan_paths(config.memory_root)
    script = build_geometry_join_plan_script(report_path)
    save_geometry_join_plan_script(script_path, script)

    await ctx.reply(
        "🧩 สร้าง Geometry Join Planner แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดล v4 อยู่ ระบบจะวิเคราะห์คู่ชิ้นส่วนโลหะและวางแผนเท่านั้น\n"
        "ไม่มี Boolean, ไม่มีการลบหรือขยับวัตถุ และไม่มีการ Export ไฟล์ผลิต\n"
        f"Join Plan JSON: {report_path}",
        file=discord.File(Path(script_path)),
    )
