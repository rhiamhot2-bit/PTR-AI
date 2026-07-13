"""Handler for !cadproduction."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.production_readiness_generator import (
    build_production_readiness_script,
    prepare_production_audit_paths,
    save_production_readiness_script,
)


async def cadproduction_command(
    ctx: commands.Context, *, request: str | None = None
) -> None:
    """Attach a report-only Rhino audit for the currently open model."""
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script_path, audit_path = prepare_production_audit_paths(config.memory_root)
    script = build_production_readiness_script(audit_path)
    save_production_readiness_script(script_path, script)

    await ctx.reply(
        "🔎 สร้าง Production Readiness Validator แล้ว\n"
        "รันไฟล์นี้ใน Rhino ที่เปิดโมเดล v4 อยู่ ระบบจะตรวจและรายงานเท่านั้น\n"
        "ไม่มี Boolean, ไม่มีการลบวัตถุ และไม่ Export STL/ไฟล์ผลิต\n"
        f"Production Audit JSON: {audit_path}",
        file=discord.File(Path(script_path)),
    )
