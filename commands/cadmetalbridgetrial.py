"""Handler for !cadmetalbridgetrial."""

from pathlib import Path

import discord
from discord.ext import commands

from utils.safe_metal_bridge_trial_generator import (
    prepare_safe_metal_bridge_trial,
    save_safe_metal_bridge_trial,
)


async def cadmetalbridgetrial_command(ctx: commands.Context) -> None:
    """Generate a preview-only Rhino Safe Metal Bridge Trial."""
    memory_root = Path(ctx.bot.ptr_config.memory_root)
    script_path, report_path, script = prepare_safe_metal_bridge_trial(memory_root)
    save_safe_metal_bridge_trial(script_path, script)

    await ctx.reply(
        "🌉 สร้าง Safe Metal Bridge Trial แล้ว\n"
        "รันใน Rhino เพื่อสร้างแท่งเชื่อมทดลองสีส้มบนเลเยอร์ PTR_METAL_BRIDGE_TRIAL\n"
        "ไม่ขยับ ไม่ลบ และไม่ Boolean ชิ้นงานต้นฉบับ; ห้ามใช้แท่งทดลองส่งผลิต\n"
        f"Bridge Trial Report: {report_path}",
        file=discord.File(script_path),
    )
