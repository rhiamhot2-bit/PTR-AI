"""Handler for !cadproductioncandidate."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.clean_production_candidate_generator import (
    prepare_clean_production_candidate,
    save_clean_production_candidate,
)

async def cadproductioncandidate_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_clean_production_candidate(root)
    save_clean_production_candidate(path,script)
    await ctx.reply(
        "🟡 สร้าง Clean Production Candidate แบบ Review Only แล้ว\n"
        "คัดลอกเฉพาะ Full Assembly Result ที่ผ่าน Screening ไม่รวมพลอย\n"
        "ยังไม่ Export และต้องตรวจงานผลิตโดยช่างมืออาชีพ\n"
        f"Candidate Report: {report}",
        file=discord.File(path),
    )
