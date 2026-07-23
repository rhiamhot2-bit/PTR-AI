"""Handler for the !content command."""

from __future__ import annotations

from typing import Any

from discord.ext import commands

from utils.content_request import build_content_brief
from webhook.client import send_to_n8n

_USAGE = (
    "กรุณาระบุเรื่องที่ต้องการทำคอนเทนต์\n"
    "ตัวอย่าง: `!content คลิป 45 วินาที เรื่อง AI ช่วยตรวจงานจิวเวลรี่ สำหรับ TikTok`"
)


async def content_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Create a review-first multi-platform content brief and send it to n8n."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(_USAGE)
        return

    brief = build_content_brief(prompt)
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    payload: dict[str, Any] = {
        "command": "content",
        "prompt": prompt,
        "business": "jewelry",
        "content_brief": brief.to_dict(),
        "required_sections": [
            "title",
            "hook",
            "spoken_script_th",
            "scene_plan",
            "caption",
            "hashtags",
            "platform_versions",
            "approval_status",
        ],
        "discord": {
            "user_id": str(ctx.author.id),
            "user_name": str(ctx.author),
            "channel_id": str(ctx.channel.id),
            "guild_id": str(ctx.guild.id) if ctx.guild else None,
            "message_id": str(ctx.message.id),
        },
    }

    async with ctx.typing():
        result = await send_to_n8n(
            config.n8n_webhook_url,
            payload,
            config.request_timeout_seconds,
        )

    if not result.get("ok"):
        error = result.get("message") or "ไม่สามารถติดต่อ Content Agent ได้"
        await ctx.reply(f"⚠️ **Content Agent V1**\n{error}"[:2000])
        return

    message = result.get("reply") or result.get("message")
    if not message:
        platforms = ", ".join(brief.platforms)
        message = (
            "ส่งคำขอไปยัง n8n สำเร็จแล้ว\n"
            f"แพลตฟอร์ม: {platforms}\n"
            "สถานะ: รอตรวจและอนุมัติก่อนเผยแพร่"
        )

    await ctx.reply(f"✅ **Content Agent V1**\n{message}"[:2000])
