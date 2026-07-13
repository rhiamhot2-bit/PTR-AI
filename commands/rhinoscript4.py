"""Handler for !rhinoscript4."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.cad_rules import format_validation_report, validate_cad_request
from utils.rhino_export_v4_generator import (
    build_rhino_export_v4_script,
    prepare_v4_paths,
    save_v4_script,
)


async def rhinoscript4_command(ctx: commands.Context, *, request: str | None = None) -> None:
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply("ใช้รายละเอียดชุดเดียวกับ !cadcheck แล้วเปลี่ยนคำสั่งเป็น !rhinoscript4")
        return
    report = validate_cad_request(prompt)
    if report["overall_status"] != "ready_for_rhino":
        await ctx.reply(
            f"{format_validation_report(report)}\n"
            "ยังไม่สร้าง Export v4 Script กรุณาแก้ข้อมูลให้ผ่านทุกข้อ"
        )
        return

    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    script_path, output_3dm, output_audit = prepare_v4_paths(config.memory_root)
    script = build_rhino_export_v4_script(report, output_3dm, output_audit)
    save_v4_script(script_path, script)
    await ctx.reply(
        "✅ สร้าง Rhino Export v4 Script แล้ว\n"
        "เมื่อรันใน Rhino จะตรวจ Closed Solid + Naked Edges และบันทึก 3DM "
        "เฉพาะเมื่อทุกชิ้นผ่าน\n"
        f"เป้าหมาย 3DM: {output_3dm}\nAudit JSON: {output_audit}",
        file=discord.File(Path(script_path)),
    )
