"""Handler for !cadfullreadiness."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.full_assembly_readiness_audit_generator import (
    prepare_full_assembly_readiness_audit,
    save_full_assembly_readiness_audit,
)

async def cadfullreadiness_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_full_assembly_readiness_audit(root)
    save_full_assembly_readiness_audit(path,script)
    await ctx.reply(
        "📋 สร้าง Full Assembly Manufacturing Readiness Audit แล้ว\n"
        "ตรวจ topology, volume, center offset, member size และ Stone collision\n"
        "เป็น Screening เท่านั้น ไม่แก้หรือ Export โมเดล และยังต้องตรวจโดยช่างมืออาชีพ\n"
        f"Audit Report: {report}",
        file=discord.File(path),
    )
