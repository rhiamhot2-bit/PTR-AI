"""Handler for !cadcorrectedfullmetalboolean."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.corrected_full_metal_assembly_boolean_rehearsal_generator import (
    prepare_corrected_full_metal_assembly_boolean_rehearsal,
    save_corrected_full_metal_assembly_boolean_rehearsal,
)

async def cadcorrectedfullmetalboolean_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_corrected_full_metal_assembly_boolean_rehearsal(root)
    save_corrected_full_metal_assembly_boolean_rehearsal(path,script)
    await ctx.reply(
        "🧪 สร้าง Corrected Full Metal Assembly Boolean Rehearsal แล้ว\n"
        "รวม Duplicate Brep 8 ชิ้น: Band, Seat, เตยแก้ความยาว 4 ต้น และ Curved Supports 2 ข้าง\n"
        "ต้นฉบับไม่ถูกแก้หรือลบ และ Production Export ยังถูก Block\n"
        f"Assembly Report: {report}",
        file=discord.File(path),
    )
