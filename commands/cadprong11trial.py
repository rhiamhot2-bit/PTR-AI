"""Handler for !cadprong11trial."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.prong_11deg_copy_trial_generator import prepare_prong_11deg_copy_trial,save_prong_11deg_copy_trial
async def cadprong11trial_command(ctx: commands.Context)->None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_prong_11deg_copy_trial(root)
    save_prong_11deg_copy_trial(path,script)
    await ctx.reply("🔵 สร้าง Prong 11° Copy Trial แล้ว\nCopy เตย 4 ต้น หมุนถึงมุมสุดท้าย 11° และขยับสำเนาให้กินกะเปาะ 25%\nต้นฉบับไม่ถูกหมุนหรือย้าย\n"+f"Trial Report: {report}",file=discord.File(path))
