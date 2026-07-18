"""Handler for !cadprong11check."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_11deg_trial_validator_generator import (
    prepare_prong_11deg_trial_validator,
    save_prong_11deg_trial_validator,
)

async def cadprong11check_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_prong_11deg_trial_validator(root)
    save_prong_11deg_trial_validator(path, script)
    await ctx.reply(
        "🔎 สร้าง Prong 11° Trial Validator แล้ว\n"
        "ตรวจเตยสำเนา 4 ต้น: เอียงออก 11°, สมมาตร, กินกะเปาะอย่างน้อย 25% และไม่ชนพลอย\n"
        "รายงานอย่างเดียว ไม่ขยับ ไม่ Boolean และไม่ Export\n"
        f"Validation Report: {report}",
        file=discord.File(path),
    )
