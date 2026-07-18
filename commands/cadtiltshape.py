"""Handler for !cadtiltshape."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_tilt_support_shape_analyzer_generator import (
    prepare_prong_tilt_support_shape_analyzer,
    save_prong_tilt_support_shape_analyzer,
)
async def cadtiltshape_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_prong_tilt_support_shape_analyzer(root)
    save_prong_tilt_support_shape_analyzer(path, script)
    await ctx.reply(
        "📏 สร้าง Prong Tilt & Support Shape Analyzer แล้ว\n"
        "วัดมุมเตยปัจจุบันเทียบเป้าหมาย 11° และตรวจเสายึดตรง/โค้งจากแนวศูนย์กลาง\n"
        "ใช้ Mesh ในหน่วยความจำ ไม่แก้โมเดล\n"
        f"Tilt/Shape Report: {report}",
        file=discord.File(path),
    )
