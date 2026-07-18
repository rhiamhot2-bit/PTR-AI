"""Handler for !cadsupportcurvetrial."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.curved_support_copy_trial_generator import (
    prepare_curved_support_copy_trial,
    save_curved_support_copy_trial,
)

async def cadsupportcurvetrial_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_curved_support_copy_trial(root)
    save_curved_support_copy_trial(path,script)
    await ctx.reply(
        "🟣 สร้าง Curved Support Copy Trial แล้ว\n"
        "สร้างแท่งยึดโค้งสมมาตร 2 ข้าง ให้ปลายบนเข้า Stone Seat และปลายล่างเข้า Ring Band\n"
        "เก็บเสาตรงต้นฉบับไว้ ไม่ Boolean และไม่ Export\n"
        f"Trial Report: {report}",
        file=discord.File(path),
    )
