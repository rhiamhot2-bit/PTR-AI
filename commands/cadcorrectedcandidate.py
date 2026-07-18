"""Handler for !cadcorrectedcandidate."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.corrected_clean_production_candidate_generator import (
    prepare_corrected_clean_production_candidate,
    save_corrected_clean_production_candidate,
)

async def cadcorrectedcandidate_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_corrected_clean_production_candidate(root)
    save_corrected_clean_production_candidate(path,script)
    await ctx.reply(
        "🟡 สร้าง Corrected Clean Production Candidate Trial แล้ว\n"
        "คัดลอกเฉพาะ Corrected Full Assembly ที่ผ่านการตรวจ เป็นชิ้น Review แยกต่างหาก\n"
        "ไม่แก้ต้นฉบับ ไม่ Boolean ไม่รวมพลอย และยังปิด Production Export\n"
        f"Candidate Report: {report}",
        file=discord.File(path),
    )
