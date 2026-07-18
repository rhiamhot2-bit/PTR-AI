"""Handler for !cadrepositionplan."""

from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_support_reposition_planner_generator import (
    prepare_prong_support_reposition_planner,
    save_prong_support_reposition_planner,
)

async def cadrepositionplan_command(ctx: commands.Context) -> None:
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_prong_support_reposition_planner(memory_root)
    save_prong_support_reposition_planner(script_path, script)
    await ctx.reply(
        "📐 สร้าง Prong 11° & Curved Support Reposition Planner แล้ว\n"
        "เตยขนาดคงที่ เอียงออก 11° ฐานกินกะเปาะอย่างน้อย 25%; เสาโค้งชนเต็มสองปลาย\n"
        "Bridge Connector ถูกเก็บเป็นวิธีสำรอง รายงานนี้ไม่แก้โมเดล\n"
        f"Reposition Plan: {report_path}",
        file=discord.File(script_path),
    )
