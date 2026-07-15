"""Handler for !cadshoulderbuild."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.shoulder_geometry_generator import (
    build_shoulder_geometry_script,
    prepare_shoulder_geometry_paths,
    save_shoulder_geometry_script,
)


async def cadshoulderbuild_command(
    ctx: commands.Context, *, request: str | None = None
) -> None:
    """Attach a Rhino script that creates two review-only shoulder solids."""
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script_path, report_path = prepare_shoulder_geometry_paths(config.memory_root)
    script = build_shoulder_geometry_script(report_path)
    save_shoulder_geometry_script(script_path, script)

    await ctx.reply(
        "🧩 สร้าง Shoulder Loft v4 แล้ว\n"
        "รันใน Rhino ที่เปิดโมเดล v4 อยู่ ระบบจะสร้างไหล่ด้วย Loft จากหน้าตัดวงรี 5 ช่วง ฐานกว้างแต่บางและไล่เรียวเข้าหาฐานกระเปาะ\n"
        "ชิ้นซ้าย–ขวายังคงแยกกันบน layer PTR_SHOULDER_REVIEW พร้อมบันทึก anchor และ clearance แบบ conservative\n"
        "ไม่มี Boolean, ไม่ลบหรือขยับชิ้นงานเดิม และไม่มี Production Export\n"
        f"Shoulder Build JSON: {report_path}",
        file=discord.File(Path(script_path)),
    )
