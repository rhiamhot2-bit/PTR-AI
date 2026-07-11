"""Handler for the !rhinoscript command."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.cad_rules import format_validation_report, validate_cad_request
from utils.rhino_script_generator import build_rhino_ring_script, save_rhino_script


async def rhinoscript_command(
    ctx: commands.Context,
    *,
    request: str | None = None,
) -> None:
    """Validate a ring request and generate a reviewable Rhino 8 Python file."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(
            "กรุณาใส่รายละเอียดครบ เช่น !rhinoscript แหวนไซซ์ 52 ทอง 18K "
            "มรกต Oval 8x6 มม. หนามเตย 4 เตย ก้านกว้าง 2.5 มม. "
            "ก้านหนา 1.8 มม. หนามเตยหนา 0.7 มม. ระยะเผื่อฝัง 0.1 มม. "
            "หัวแหวนสูง 6.5 มม."
        )
        return

    report = validate_cad_request(prompt)
    if report["overall_status"] != "ready_for_rhino":
        await ctx.reply(
            f"{format_validation_report(report)}\n"
            "ยังไม่สร้างไฟล์ Rhino Script กรุณาแก้ข้อมูลให้ผ่านทุกข้อ"
        )
        return

    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script = build_rhino_ring_script(report)
    path = save_rhino_script(config.memory_root, report, script)
    await ctx.reply(
        "✅ สร้าง Rhino 8 Python Script รุ่นแรกแล้ว\n"
        "ไฟล์นี้สร้างวงแหวน ก้านแบบหน้าตัดวงรี และพลอยตัวแทนเท่านั้น\n"
        "ต้องให้ช่างตรวจใน Rhino ก่อนผลิตจริง",
        file=discord.File(Path(path)),
    )
