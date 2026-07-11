"""Handler for !rhinoscript2."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.cad_rules import format_validation_report, validate_cad_request
from utils.rhino_setting_v2_generator import (
    build_rhino_setting_v2_script,
    save_rhino_setting_v2_script,
)


async def rhinoscript2_command(ctx: commands.Context, *, request: str | None = None) -> None:
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply("ใช้รายละเอียดชุดเดียวกับ !cadcheck แล้วเปลี่ยนคำสั่งเป็น !rhinoscript2")
        return
    report = validate_cad_request(prompt)
    if report["overall_status"] != "ready_for_rhino":
        await ctx.reply(
            f"{format_validation_report(report)}\n"
            "ยังไม่สร้าง Setting v2 Script กรุณาแก้ข้อมูลให้ผ่านทุกข้อ"
        )
        return
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script = build_rhino_setting_v2_script(report)
    path = save_rhino_setting_v2_script(config.memory_root, script)
    await ctx.reply(
        "✅ สร้าง Rhino Setting v2 Concept แล้ว: Stone Seat + 4 Prongs + Basket Supports\n"
        "ต้องตรวจและปรับใน Rhino ก่อนผลิตจริง",
        file=discord.File(Path(path)),
    )
