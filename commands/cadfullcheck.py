"""Handler for !cadfullcheck."""
from pathlib import Path
import discord
from discord.ext import commands
from utils.job_profile import load_profile, parse_profile_arguments, normalized_profile, validate_profile
from utils.cad_full_check_generator import prepare_cad_full_check, save_cad_full_check

async def cadfullcheck_command(ctx: commands.Context, *arguments: str) -> None:
    root=Path(ctx.bot.ptr_config.memory_root)
    profile_path=root/"Job_Profiles"/"current.json"
    if not profile_path.exists():
        await ctx.reply("JOB_PROFILE_REQUIRED: กรุณาสร้างด้วย !cadprofile key=value ... ก่อน")
        return
    profile=load_profile(profile_path)
    overrides,errors=parse_profile_arguments(arguments)
    profile.update(overrides)
    errors += validate_profile(profile)
    if errors:
        await ctx.reply("JOB_PROFILE_INVALID\n"+"\n".join("- "+e for e in errors))
        return
    profile=normalized_profile(profile)
    path,report,script=prepare_cad_full_check(root,profile)
    save_cad_full_check(path,script)
    await ctx.reply("🔍 สร้าง Parameterized CAD Full Check แล้ว\nตรวจตาม JOB_PROFILE โดยไม่ย้าย ไม่ลบ และไม่ Union ชิ้นงานต้นฉบับ\nงานผ่านแล้วยังคงแยกชิ้นเพื่อแก้ไข และให้ Union เองตอนจบ\nFull Check Report: "+str(report),file=discord.File(path))
