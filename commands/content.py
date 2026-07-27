"""Handler for the !content command."""

from __future__ import annotations

from typing import Any

from discord.ext import commands

from utils.content_request import build_content_brief
from webhook.client import send_to_n8n

_USAGE = (
    "กรุณาระบุเรื่องที่ต้องการทำคอนเทนต์\n"
    "ตัวอย่าง: `!content คลิปสอน 45 วินาที เรื่อง AI ช่วยตรวจงานจิวเวลรี่ สำหรับ TikTok`"
)

_REQUIRED_SECTIONS = [
    "content_analysis",
    "title",
    "hook",
    "spoken_script_th",
    "timeline",
    "scene_plan",
    "image_prompt",
    "veo_prompt",
    "thumbnail_prompt",
    "platform_captions",
    "platform_hashtags",
    "cta",
    "production_guide",
    "quality_review",
    "approval_status",
]


async def content_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Create a review-first Content Package V2 and send it to n8n."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(_USAGE)
        return

    brief = build_content_brief(prompt)
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    payload: dict[str, Any] = {
        "command": "content",
        "agent_version": "2.0",
        "prompt": prompt,
        "business": "jewelry",
        "content_brief": brief.to_dict(),
        "required_sections": _REQUIRED_SECTIONS,
        "generation_rules": {
            "presenter": "คุณเทียม",
            "assistant_persona": "PTR AI",
            "human_first": True,
            "spoken_language": "thai",
            "veo_scene_seconds": 8,
            "no_on_screen_text": True,
            "no_subtitles": True,
            "no_logo": True,
            "no_watermark": True,
            "approval_before_publish": True,
        },
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
        await ctx.reply(f"⚠️ **Content Agent V2**\n{error}"[:2000])
        return

    message = result.get("reply") or result.get("message")
    if not message:
        platforms = ", ".join(brief.platforms)
        styles = ", ".join(brief.styles)
        message = (
            "ส่งคำขอ Content Package V2 ไปยัง n8n สำเร็จแล้ว\n"
            f"แพลตฟอร์ม: {platforms}\n"
            f"สไตล์: {styles}\n"
            "ผลลัพธ์: Script + Image Prompt + Veo Prompt + Thumbnail + Caption + Review\n"
            "สถานะ: รอตรวจและอนุมัติก่อนเผยแพร่"
        )

    await ctx.reply(f"✅ **Content Agent V2**\n{message}"[:2000])
