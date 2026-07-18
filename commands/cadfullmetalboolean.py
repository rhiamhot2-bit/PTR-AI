"""Handler for !cadfullmetalboolean."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.full_metal_assembly_boolean_rehearsal_generator import (
    prepare_full_metal_assembly_boolean_rehearsal,
    save_full_metal_assembly_boolean_rehearsal,
)

async def cadfullmetalboolean_command(ctx: commands.Context) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    path,report,script=prepare_full_metal_assembly_boolean_rehearsal(root)
    save_full_metal_assembly_boolean_rehearsal(path,script)
    await ctx.reply(
        "🧪 สร้าง Full Metal Assembly Boolean Rehearsal แล้ว\n"
        "รวม Duplicate Brep 8 ชิ้น: Band, Seat, เตย 11° สี่ต้น และ Curved Supports สองข้าง\n"
        "ต้นฉบับไม่ถูกแก้หรือลบ และ Production Export ยังถูก Block\n"
        f"Assembly Report: {report}",
        file=discord.File(path),
    )
