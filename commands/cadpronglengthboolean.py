"""Handler for !cadpronglengthboolean."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_length_correction_boolean_rehearsal_generator import (
    prepare_prong_length_correction_boolean_rehearsal,
    save_prong_length_correction_boolean_rehearsal,
)

async def cadpronglengthboolean_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_prong_length_correction_boolean_rehearsal(root)
    save_prong_length_correction_boolean_rehearsal(path, script)
    await ctx.reply(
        "🧩 สร้าง Prong Length Correction Boolean Rehearsal แล้ว\n"
        "ทดลองรวมกะเปาะกับสำเนาเตยแก้ความยาว 4 ต้น โดยใช้ Duplicate Breps เท่านั้น\n"
        "ไม่แก้หรือลบต้นฉบับ และไม่ Export\n"
        f"Rehearsal Report: {report}",
        file=discord.File(path),
    )
