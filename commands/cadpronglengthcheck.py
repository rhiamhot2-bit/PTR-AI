"""Handler for !cadpronglengthcheck."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_length_correction_validator_generator import (
    prepare_prong_length_correction_validator,
    save_prong_length_correction_validator,
)

async def cadpronglengthcheck_command(ctx: commands.Context) -> None:
    root = Path(ctx.bot.ptr_config.memory_root)
    path, report, script = prepare_prong_length_correction_validator(root)
    save_prong_length_correction_validator(path, script)
    await ctx.reply(
        "✅ สร้าง Prong Length Correction Validator แบบ Report Only แล้ว\n"
        "ตรวจระยะปลายเตย ฐาน มุมเอียง เส้นผ่านศูนย์กลาง ความสมมาตร และการชนพลอย\n"
        "ไม่แก้โมเดล ไม่ Boolean และไม่ Export\n"
        f"Validation Report: {report}",
        file=discord.File(path),
    )
