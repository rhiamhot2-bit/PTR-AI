"""Handler for !cadfinishingaudit."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.production_finishing_audit_generator import (
    prepare_production_finishing_audit,
    save_production_finishing_audit,
)

async def cadfinishingaudit_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_production_finishing_audit(root)
    save_production_finishing_audit(path, script)
    await ctx.reply(
        "🔍 สร้าง Production Finishing Audit แบบ Report Only แล้ว\n"
        "ตรวจความสูงเตย ความสมมาตร เสาโค้ง ความหนา และช่องใส่พลอย\n"
        "ไม่แก้โมเดล ไม่ Boolean และไม่ Export\n"
        f"Finishing Report: {report}",
        file=discord.File(path),
    )
