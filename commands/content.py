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

_CANONICAL_OUTPUT_FIELDS = [
    "request_id",
    "mode",
    "platform",
    "objective",
    "audience",
    "language",
    "status",
    "core_message",
    "hook",
    "script",
    "caption",
    "cta",
    "keywords",
    "hashtags",
    "scene_plan",
    "asset_requirements",
    "image_prompt",
    "thumbnail_prompt",
    "video_prompt",
    "production_notes",
    "accuracy_notes",
    "risks",
    "human_approval_required",
    "approval_reason",
]

_COMPATIBILITY_MAPPING = {
    "content_analysis": "objective/audience/core_message",
    "spoken_script_th": "script",
    "timeline": "scene_plan",
    "veo_prompt": "video_prompt",
    "platform_captions": "caption",
    "platform_hashtags": "hashtags",
    "production_guide": "production_notes",
    "quality_review": "accuracy_notes/risks",
    "approval_status": "status",
}


async def content_command(ctx: commands.Context, *, request: str | None = None) -> None:
    """Create a review-first content package aligned with PTR-CONTENT-STD v2.0."""
    prompt = (request or "").strip()
    if not prompt:
        await ctx.reply(_USAGE)
        return

    brief = build_content_brief(prompt)
    config = ctx.bot.ptr_config  # type: ignore[attr-defined]
    payload: dict[str, Any] = {
        "command": "content",
        "agent_version": "2.1-integration",
        "contract": "CONTENT-OUTPUT-CONTRACT-v1.0",
        "prompt": prompt,
        "business": "jewelry",
        "content_brief": brief.to_dict(),
        "canonical_output_fields": _CANONICAL_OUTPUT_FIELDS,
        "compatibility_mapping": _COMPATIBILITY_MAPPING,
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
            "auto_publish": False,
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
        await ctx.reply(f"⚠️ **Content Agent V2 Integration**\n{error}"[:2000])
        return

    message = result.get("reply") or result.get("message")
    if not message:
        platforms = ", ".join(brief.platforms)
        styles = ", ".join(brief.styles)
        message = (
            "ส่งคำขอ Content Package ไปยัง n8n สำเร็จแล้ว\n"
            f"แพลตฟอร์ม: {platforms}\n"
            f"สไตล์: {styles}\n"
            f"สิทธิ์เนื้อหา: {brief.access_tier}\n"
            "มาตรฐาน: PTR-CONTENT-STD v2.0\n"
            "สถานะ: needs_review — รอผู้ก่อตั้งตรวจและอนุมัติก่อนเผยแพร่"
        )

    await ctx.reply(f"✅ **Content Agent V2 Integration**\n{message}"[:2000])
