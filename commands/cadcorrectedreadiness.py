"""Handler for !cadcorrectedreadiness."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.corrected_full_assembly_readiness_audit_generator import (
    prepare_corrected_full_assembly_readiness_audit,
    save_corrected_full_assembly_readiness_audit,
)

async def cadcorrectedreadiness_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_corrected_full_assembly_readiness_audit(root)
    save_corrected_full_assembly_readiness_audit(path,script)
    await ctx.reply(
        "📋 สร้าง Corrected Full Assembly Manufacturing Readiness Audit แล้ว\n"
        "ตรวจ topology, volume, center offset, member size และ Stone collision ของผลรวมที่แก้ไขล่าสุด\n"
        "เป็น Screening เท่านั้น ไม่แก้หรือ Export โมเดล และยังต้องตรวจโดยช่างมืออาชีพ\n"
        f"Audit Report: {report}",
        file=discord.File(path),
    )
