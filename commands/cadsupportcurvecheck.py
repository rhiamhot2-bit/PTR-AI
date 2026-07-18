"""Handler for !cadsupportcurvecheck."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.curved_support_contact_validator_generator import (
    prepare_curved_support_contact_validator,
    save_curved_support_contact_validator,
)

async def cadsupportcurvecheck_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_curved_support_contact_validator(root)
    save_curved_support_contact_validator(path,script)
    await ctx.reply(
        "🔎 สร้าง Curved Support Contact Validator แล้ว\n"
        "ตรวจ Closed Solid, Naked Edge, การเข้าเนื้อกะเปาะ/ก้านแหวน และความสมมาตร\n"
        "วิเคราะห์ Intersection ในหน่วยความจำ ไม่แก้โมเดลและไม่ Export\n"
        f"Contact Report: {report}",
        file=discord.File(path),
    )
