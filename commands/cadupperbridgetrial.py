"""Handler for !cadupperbridgetrial."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.upper_contact_bridge_trial_generator import (
    prepare_upper_contact_bridge_trial,
    save_upper_contact_bridge_trial,
)


async def cadupperbridgetrial_command(ctx: commands.Context) -> None:
    """Generate a preview-only Rhino Upper Contact Bridge Trial."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_upper_contact_bridge_trial(memory_root)
    save_upper_contact_bridge_trial(script_path, script)

    await ctx.reply(
        "🩷 สร้าง Upper Contact Bridge Trial แล้ว\n"
        "สร้างแท่งทดลองสีชมพู 6 ชิ้นตามจุดผิวจริงบนเลเยอร์แยก\n"
        "ไม่ขยับและไม่ Boolean กะเปาะ เตย หรือ Basket Support ต้นฉบับ\n"
        f"Upper Bridge Report: {report_path}",
        file=discord.File(script_path),
    )
