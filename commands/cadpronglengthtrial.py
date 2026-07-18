"""Handler for !cadpronglengthtrial."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_length_correction_trial_generator import (
    prepare_prong_length_correction_trial,
    save_prong_length_correction_trial,
)

async def cadpronglengthtrial_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_prong_length_correction_trial(root)
    save_prong_length_correction_trial(path, script)
    await ctx.reply(
        "🧪 สร้าง Prong Length Correction Trial แล้ว\n"
        "เพิ่มเฉพาะปลายสำเนาเตยตามแนวแกน รักษาฐาน ขนาด และมุมเอียงออก 11°\n"
        "ไม่แก้ Candidate ต้นฉบับ ไม่ Boolean และไม่ Export\n"
        f"Trial Report: {report}",
        file=discord.File(path),
    )
