"""Discord command for generating a contact-audited Shoulder Loft v4 script."""

import logging

import discord
from discord.ext import commands

from config import MEMORY_ROOT
from utils.shoulder_loft_v4_generator import (
    build_shoulder_loft_v4_script,
    prepare_shoulder_loft_v4_paths,
    save_shoulder_loft_v4_script,
)

logger = logging.getLogger("ptr_ai")


def register(bot: commands.Bot):
    @bot.command(name="cadshoulderloft4")
    async def cadshoulderloft4(ctx: commands.Context):
        try:
            script_path, report_path = prepare_shoulder_loft_v4_paths(MEMORY_ROOT)
            script = build_shoulder_loft_v4_script(report_path)
            save_shoulder_loft_v4_script(script, script_path)

            message = (
                "✅ สร้าง Shoulder Loft v4 + Contact Audit แล้ว\n"
                "สคริปต์จะสร้าง Shoulder ซ้าย–ขวาแบบ 5 หน้าตัด "
                "และตรวจ Brep intersection จริงกับก้านแหวนและกะเปาะ\n"
                "ต้องให้ทั้งสองข้างชนทั้ง band และ setting จึงจะขึ้น contact_verified=true\n"
                "ไม่มี Boolean, ไม่ลบหรือแก้ source geometry และไม่ Export งานผลิต\n"
                f"Contact Audit JSON: {report_path}"
            )
            await ctx.reply(
                message,
                file=discord.File(script_path),
                mention_author=False,
            )
        except Exception:
            logger.exception("Failed to generate Shoulder Loft v4 contact audit")
            await ctx.reply(
                "❌ สร้าง Shoulder Loft v4 ไม่สำเร็จ กรุณาตรวจ log ของบอต",
                mention_author=False,
            )
