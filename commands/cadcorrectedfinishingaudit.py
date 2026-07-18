"""Handler for !cadcorrectedfinishingaudit."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.corrected_production_finishing_audit_generator import (
    prepare_corrected_production_finishing_audit,
    save_corrected_production_finishing_audit,
)

async def cadcorrectedfinishingaudit_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_corrected_production_finishing_audit(root)
    save_corrected_production_finishing_audit(path,script)
    await ctx.reply(
        "🔍 สร้าง Corrected Production Finishing Audit แบบ Report Only แล้ว\n"
        "ตรวจเตยแก้ความยาว ระยะเผื่อตัด 0.80 mm เอียงออก 11° ความสมมาตร และรอยต่อเสาโค้ง\n"
        "ไม่แก้โมเดล ไม่ Boolean และไม่ Export\n"
        f"Corrected Finishing Report: {report}",file=discord.File(path))
