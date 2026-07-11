"""Handler for !rhinoscript3."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.cad_rules import format_validation_report, validate_cad_request
from utils.rhino_setting_v3_generator import (
    build_rhino_setting_v3_script,
    save_rhino_setting_v3_script,
)


async def rhinoscript3_command(ctx: commands.Context, *, request: str | None = None) -> None:
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply("ใช้รายละเอียดชุดเดียวกับ !cadcheck แล้วเปลี่ยนคำสั่งเป็น !rhinoscript3")
        return
    report = validate_cad_request(prompt)
    if report["overall_status"] != "ready_for_rhino":
        await ctx.reply(
            f"{format_validation_report(report)}\n"
            "ยังไม่สร้าง Setting v3 Script กรุณาแก้ข้อมูลให้ผ่านทุกข้อ"
        )
        return
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script = build_rhino_setting_v3_script(report)
    path = save_rhino_setting_v3_script(config.memory_root, script)
    await ctx.reply(
        "✅ สร้าง Rhino Setting v3 Review แล้ว: Inward Prongs + Girdle Guides + Geometry Audit\n"
        "Girdle Guides เป็นตัวช่วยตรวจ ไม่ได้ Boolean ตัดร่องอัตโนมัติ",
        file=discord.File(Path(path)),
    )
