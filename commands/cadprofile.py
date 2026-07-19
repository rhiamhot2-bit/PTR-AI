"""Handler for !cadprofile."""
from pathlib import Path
from discord.ext import commands
from utils.job_profile import parse_profile_arguments, save_profile, validate_profile

async def cadprofile_command(ctx: commands.Context, *arguments: str) -> None:
    values, errors=parse_profile_arguments(arguments)
    errors += validate_profile(values)
    if errors:
        await ctx.reply("JOB_PROFILE_INVALID\n"+"\n".join("- "+e for e in errors))
        return
    path=Path(ctx.bot.ptr_config.memory_root)/"Job_Profiles"/"current.json"
    save_profile(path,values)
    await ctx.reply("✅ บันทึก JOB_PROFILE แบบ EDITABLE_NON_UNION แล้ว\nใช้ !cadfullcheck เพื่อสร้างสคริปต์ตรวจงาน\n"+str(path))
