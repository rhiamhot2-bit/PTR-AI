"""Handler for !cadprong11boolean."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_11deg_boolean_rehearsal_generator import (
    prepare_prong_11deg_boolean_rehearsal,
    save_prong_11deg_boolean_rehearsal,
)

async def cadprong11boolean_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_prong_11deg_boolean_rehearsal(root)
    save_prong_11deg_boolean_rehearsal(path,script)
    await ctx.reply(
        "🧪 สร้าง Prong 11° Boolean Rehearsal แล้ว\n"
        "Union เฉพาะ Duplicate Brep ของกะเปาะและเตยทดลอง 4 ต้น\n"
        "ต้นฉบับไม่ถูกแก้หรือลบ และ Production Export ยังถูก Block\n"
        f"Rehearsal Report: {report}",
        file=discord.File(path),
    )
